from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd
import numpy as np
from io import StringIO
from sklearn.ensemble import IsolationForest

router = APIRouter()

# ======================================================
# SAFE CSV READER
# ======================================================

def read_csv_safe(file_bytes):
    try:
        return pd.read_csv(StringIO(file_bytes.decode("utf-8")))
    except:
        return pd.read_csv(StringIO(file_bytes.decode("latin-1")))

# ======================================================
# METRIC CALCULATIONS
# ======================================================

def calculate_completeness(df):
    total = df.size
    missing = df.isnull().sum().sum()
    if total == 0:
        return 100.0
    return round((1 - (missing / total)) * 100, 2)

def calculate_uniqueness(df):
    rows = len(df)
    if rows == 0:
        return 100.0
    duplicate_ratio = df.duplicated().sum() / rows
    return round((1 - duplicate_ratio) * 100, 2)

def calculate_outlier_penalty(df):
    numeric = df.select_dtypes(include=np.number)
    if numeric.empty:
        return 100.0

    z_scores = np.abs((numeric - numeric.mean()) / numeric.std())
    z_scores = z_scores.replace([np.inf, -np.inf], 0).fillna(0)

    outliers = (z_scores > 3).sum().sum()
    total = numeric.size

    if total == 0:
        return 100.0

    return round((1 - (outliers / total)) * 100, 2)

def calculate_consistency(df):
    numeric = df.select_dtypes(include=np.number)
    if numeric.empty:
        return 100.0
    invalid = numeric.isnull().sum().sum()
    total = numeric.size
    return round((1 - invalid / total) * 100, 2)

# ======================================================
# FINAL QUALITY SCORE
# ======================================================

def calculate_quality_score(metrics):
    weights = {
        "completeness": 0.4,
        "uniqueness": 0.25,
        "consistency": 0.2,
        "outlier_penalty": 0.15
    }

    base_score = sum(metrics[k] * weights[k] for k in metrics)

    penalty = 0
    for value in metrics.values():
        if value < 90:
            penalty += (90 - value) * 0.2

    final_score = base_score - penalty

    if final_score > 98:
        final_score = 98 + (final_score - 98) * 0.2

    return round(max(0, min(final_score, 100)), 2)

# ======================================================
# CLEANING METHODS
# ======================================================

def apply_missing_strategy(df, strategy):
    df = df.copy()
    numeric_cols = df.select_dtypes(include=np.number).columns
    categorical_cols = df.select_dtypes(exclude=np.number).columns

    if strategy == "Mean":
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    elif strategy == "Median":
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    elif strategy == "Mode":
        for col in df.columns:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])

    elif strategy == "Drop":
        df = df.dropna()

    elif strategy == "Smart":
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        for col in categorical_cols:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])

    return df

def apply_iqr(df):
    df = df.copy()
    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower) & (df[col] <= upper)]

    return df

def apply_isolation_forest(df):
    df = df.copy()
    numeric_cols = df.select_dtypes(include=np.number)

    if numeric_cols.empty:
        return df

    model = IsolationForest(contamination=0.05, random_state=42)
    preds = model.fit_predict(numeric_cols)

    return df[preds == 1]

# ======================================================
# COLUMN IMPORTANCE (FOR FRONTEND)
# ======================================================

def calculate_column_importance(df):
    importance = []
    for col in df.columns:
        importance.append({
            "column": col,
            "missing_values": int(df[col].isnull().sum()),
            "unique_values": int(df[col].nunique())
        })
    return importance

# ======================================================
# MAIN ENDPOINT
# ======================================================

@router.post("/analyze/")
async def analyze_dataset(
    file: UploadFile = File(...),
    remove_duplicates: str = Form("true"),
    missing_strategy: str = Form("Smart"),
    outlier_method: str = Form("None")
):

    remove_duplicates = remove_duplicates.lower() == "true"

    file_bytes = await file.read()
    df_original = read_csv_safe(file_bytes)
    duplicate_rows = int(df_original.duplicated().sum())
    
    # BEFORE METRICS
    before_metrics = {
        "completeness": calculate_completeness(df_original),
        "uniqueness": calculate_uniqueness(df_original),
        "consistency": calculate_consistency(df_original),
        "outlier_penalty": calculate_outlier_penalty(df_original),
    }

    before_score = calculate_quality_score(before_metrics)

    # CLEANING
    df_cleaned = df_original.copy()

    if remove_duplicates:
        df_cleaned = df_cleaned.drop_duplicates()

    df_cleaned = apply_missing_strategy(df_cleaned, missing_strategy)

    if outlier_method == "IQR":
        df_cleaned = apply_iqr(df_cleaned)
    elif outlier_method == "Isolation Forest":
        df_cleaned = apply_isolation_forest(df_cleaned)

    # AFTER METRICS
    after_metrics = {
        "completeness": calculate_completeness(df_cleaned),
        "uniqueness": calculate_uniqueness(df_cleaned),
        "consistency": calculate_consistency(df_cleaned),
        "outlier_penalty": calculate_outlier_penalty(df_cleaned),
    }

    after_score = calculate_quality_score(after_metrics)

    return {
        "before_score": before_score,
        "after_score": after_score,
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,

        # Initial dataset info
        "rows_before": int(len(df_original)),
        "columns": int(len(df_original.columns)),
        "duplicate_rows": duplicate_rows,

        # Cleaning info
        "rows_after": int(len(df_cleaned)),

        "original_preview": df_original.head(20).replace({np.nan: None}).to_dict(orient="records"),
        "cleaned_preview": df_cleaned.head(20).replace({np.nan: None}).to_dict(orient="records"),

        "column_importance": calculate_column_importance(df_cleaned)
    }