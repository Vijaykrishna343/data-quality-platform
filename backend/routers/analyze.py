from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd
import numpy as np
from io import StringIO

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
# STEP 1 HELPERS
# ======================================================

def calculate_empty_rows(df):
    df_temp = df.replace("", np.nan)
    return int(df_temp.isnull().all(axis=1).sum())


def calculate_duplicate_rows(df):
    """
    Count duplicates correctly:
    - Exclude fully empty rows
    - Keep first occurrence
    """
    df_temp = df.replace("", np.nan)
    df_temp = df_temp.dropna(how="all")
    return int(df_temp.duplicated(keep="first").sum())


def detect_order(df):
    report = {
        "is_ordered": True,
        "ordered_by": "Not detected",
        "was_auto_sorted": False,
        "message": ""
    }

    df_copy = df.copy()

    # 1️⃣ Try timestamp/date columns
    for col in df_copy.columns:
        if "time" in col.lower() or "date" in col.lower():
            try:
                temp = pd.to_datetime(df_copy[col], errors="coerce")
                if temp.is_monotonic_increasing:
                    report["ordered_by"] = col
                else:
                    df_copy = df_copy.sort_values(by=col).reset_index(drop=True)
                    report["is_ordered"] = False
                    report["ordered_by"] = col
                    report["was_auto_sorted"] = True
                    report["message"] = f"Dataset was auto-sorted by {col}"
                return df_copy, report
            except:
                pass

    # 2️⃣ Try serial/id columns
    for col in df_copy.columns:
        if "id" in col.lower() or "serial" in col.lower():
            if df_copy[col].is_monotonic_increasing:
                report["ordered_by"] = col
            else:
                df_copy = df_copy.sort_values(by=col).reset_index(drop=True)
                report["is_ordered"] = False
                report["ordered_by"] = col
                report["was_auto_sorted"] = True
                report["message"] = f"Dataset was auto-sorted by {col}"
            return df_copy, report

    return df_copy, report


def detect_sequence_gaps(df):
    report = {
        "column": None,
        "has_gaps": False,
        "missing_values": [],
        "message": ""
    }

    df_copy = df.copy()

    for col in df_copy.columns:
        if "id" in col.lower() or "serial" in col.lower():
            if pd.api.types.is_numeric_dtype(df_copy[col]):

                sorted_vals = sorted(df_copy[col].dropna().astype(int).unique())
                expected = list(range(min(sorted_vals), max(sorted_vals) + 1))

                missing = list(set(expected) - set(sorted_vals))
                missing.sort()

                report["column"] = col

                if missing:
                    report["has_gaps"] = True
                    report["missing_values"] = missing
                    report["message"] = "Sequence gaps detected."
                else:
                    report["message"] = "No sequence gaps detected."

                return report

    report["message"] = "No sequence column detected."
    return report


def handle_missing_values(df, strategy):
    df_copy = df.copy()

    if strategy == "None":
        return df_copy

    if strategy == "Drop Rows":
        return df_copy.dropna()

    numeric_cols = df_copy.select_dtypes(include=np.number).columns
    categorical_cols = df_copy.select_dtypes(exclude=np.number).columns

    if strategy == "Mean":
        for col in numeric_cols:
            df_copy[col] = df_copy[col].fillna(df_copy[col].mean())

    elif strategy == "Smart":
        for col in numeric_cols:
            df_copy[col] = df_copy[col].fillna(df_copy[col].median())

        for col in categorical_cols:
            if not df_copy[col].mode().empty:
                df_copy[col] = df_copy[col].fillna(df_copy[col].mode()[0])

    return df_copy


def repair_sequence(df):
    df_copy = df.copy()

    for col in df_copy.columns:
        if "id" in col.lower() or "serial" in col.lower():
            df_copy[col] = range(1, len(df_copy) + 1)
            break

    return df_copy

def handle_outliers(df, method):
    df_copy = df.copy()

    numeric_cols = df_copy.select_dtypes(include=np.number).columns

    if method == "None":
        return df_copy

    if method == "Z-Score":
        for col in numeric_cols:
            mean = df_copy[col].mean()
            std = df_copy[col].std()

            if std == 0:
                continue

            z_scores = (df_copy[col] - mean) / std
            df_copy.loc[np.abs(z_scores) > 3, col] = np.nan

        return df_copy

    if method == "IQR" or method == "Remove (IQR)":
        for col in numeric_cols:
            Q1 = df_copy[col].quantile(0.25)
            Q3 = df_copy[col].quantile(0.75)
            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            if method == "IQR":
                df_copy.loc[
                    (df_copy[col] < lower) | (df_copy[col] > upper),
                    col
                ] = np.nan

            elif method == "Remove (IQR)":
                df_copy = df_copy[
                    ~((df_copy[col] < lower) | (df_copy[col] > upper))
                ]

        return df_copy

    return df_copy

def generate_column_profile(df):
    profile = {}

    total_rows = len(df)

    for col in df.columns:
        col_data = df[col]

        column_info = {
            "data_type": str(col_data.dtype),
            "null_count": int(col_data.isnull().sum()),
            "null_percentage": round((col_data.isnull().sum() / total_rows) * 100, 2) if total_rows > 0 else 0,
            "unique_values": int(col_data.nunique()),
            "sample_values": col_data.dropna().unique()[:3].tolist()
        }

        if pd.api.types.is_numeric_dtype(col_data):
            column_info.update({
                "min": float(col_data.min()) if not col_data.dropna().empty else None,
                "max": float(col_data.max()) if not col_data.dropna().empty else None,
                "mean": float(col_data.mean()) if not col_data.dropna().empty else None,
                "median": float(col_data.median()) if not col_data.dropna().empty else None,
            })

        profile[col] = column_info

    return profile

def calculate_data_drift(df_before, df_after, before_score, after_score):
    drift_report = {}

    rows_before = len(df_before)
    rows_after = len(df_after)

    drift_report["row_change"] = {
        "before": rows_before,
        "after": rows_after,
        "difference": rows_before - rows_after,
        "percentage_change": round(((rows_before - rows_after) / rows_before) * 100, 2) if rows_before > 0 else 0
    }

    missing_before = df_before.isnull().sum().sum()
    missing_after = df_after.isnull().sum().sum()

    drift_report["missing_value_change"] = {
        "before": int(missing_before),
        "after": int(missing_after),
        "difference": int(missing_before - missing_after)
    }

    drift_report["score_change"] = {
        "before": before_score,
        "after": after_score,
        "improvement": round(after_score - before_score, 2)
    }

    return drift_report

def generate_insights(before_score, after_score, drift_report, sequence_report):
    insights = {
        "quality_status": "",
        "summary": "",
        "warnings": [],
        "suggestions": []
    }

    improvement = after_score - before_score

    # Quality Level
    if after_score >= 90:
        insights["quality_status"] = "Excellent"
    elif after_score >= 75:
        insights["quality_status"] = "Good"
    elif after_score >= 50:
        insights["quality_status"] = "Moderate"
    else:
        insights["quality_status"] = "Poor"

    # Summary
    if improvement > 0:
        insights["summary"] = f"Data quality improved by {round(improvement,2)} points after cleaning."
    elif improvement < 0:
        insights["summary"] = "Data quality decreased after cleaning. Review cleaning strategy."
    else:
        insights["summary"] = "No significant change in data quality."

    # Warnings
    if drift_report["row_change"]["difference"] > 0:
        insights["warnings"].append(
            f"{drift_report['row_change']['difference']} rows were removed during cleaning."
        )

    if sequence_report["has_gaps"]:
        insights["warnings"].append("Sequence gaps were detected in ID column.")

    # Suggestions
    if after_score < 80:
        insights["suggestions"].append("Consider applying outlier handling or stricter missing value strategy.")

    if drift_report["missing_value_change"]["after"] > 0:
        insights["suggestions"].append("There are still missing values present in the dataset.")

    return insights

# ======================================================
# METRICS (UNCHANGED)
# ======================================================

def calculate_completeness(df):
    total = df.size
    missing = df.isnull().sum().sum()
    return 100.0 if total == 0 else round((1 - (missing / total)) * 100, 2)


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
    return 100.0 if total == 0 else round((1 - (outliers / total)) * 100, 2)


def calculate_consistency(df):
    numeric = df.select_dtypes(include=np.number)
    if numeric.empty:
        return 100.0
    invalid = numeric.isnull().sum().sum()
    total = numeric.size
    return round((1 - invalid / total) * 100, 2)


def calculate_quality_score(metrics):
    weights = {
        "completeness": 0.4,
        "uniqueness": 0.25,
        "consistency": 0.2,
        "outlier_penalty": 0.15
    }

    base_score = sum(metrics[k] * weights[k] for k in metrics)
    penalty = sum((90 - v) * 0.2 for v in metrics.values() if v < 90)
    final_score = base_score - penalty

    if final_score > 98:
        final_score = 98 + (final_score - 98) * 0.2

    return round(max(0, min(final_score, 100)), 2)

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

    # STEP 1 DETECTION
    empty_rows = calculate_empty_rows(df_original)
    duplicate_rows = calculate_duplicate_rows(df_original)

    # Detect order
    df_original, order_report = detect_order(df_original)

    # Detect sequence gaps
    sequence_report = detect_sequence_gaps(df_original)

    # BEFORE METRICS
    before_metrics = {
        "completeness": calculate_completeness(df_original),
        "uniqueness": calculate_uniqueness(df_original),
        "consistency": calculate_consistency(df_original),
        "outlier_penalty": calculate_outlier_penalty(df_original),
    }

    before_score = calculate_quality_score(before_metrics)

    # ======================================================
    # CLEANING
    # ======================================================

    df_cleaned = df_original.copy()

    # Remove fully empty rows
    df_cleaned = df_cleaned.replace("", np.nan)
    df_cleaned = df_cleaned.dropna(how="all")

    # Apply missing strategy
    df_cleaned = handle_missing_values(df_cleaned, missing_strategy)
    # Apply outlier handling
    df_cleaned = handle_outliers(df_cleaned, outlier_method)
    # Remove duplicates
    if remove_duplicates:
        df_cleaned = df_cleaned.drop_duplicates(keep="first")

    # Repair sequence
    df_cleaned = repair_sequence(df_cleaned)

    # AFTER METRICS
    after_metrics = {
        "completeness": calculate_completeness(df_cleaned),
        "uniqueness": calculate_uniqueness(df_cleaned),
        "consistency": calculate_consistency(df_cleaned),
        "outlier_penalty": calculate_outlier_penalty(df_cleaned),
    }

    after_score = calculate_quality_score(after_metrics)
    column_profile = generate_column_profile(df_cleaned)
    drift_report = calculate_data_drift(
    df_original,
    df_cleaned,
    before_score,
    after_score
    )

    insights = generate_insights(
    before_score,
    after_score,
    drift_report,
    sequence_report
    )
    return {
        "before_score": before_score,
        "after_score": after_score,
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "insights": insights,
        "data_drift": drift_report,
    
        "rows_before": int(len(df_original)),
        "columns": int(len(df_original.columns)),
        "duplicate_rows": duplicate_rows,
        "empty_rows": empty_rows,
        "order_report": order_report,
        "sequence_report": sequence_report,

        "column_profile": column_profile,

        "rows_after": int(len(df_cleaned)),

        "original_preview": df_original.head(20).replace({np.nan: None}).to_dict(orient="records"),
        "cleaned_preview": df_cleaned.head(20).replace({np.nan: None}).to_dict(orient="records"),
    }