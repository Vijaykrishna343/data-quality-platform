from fastapi import APIRouter, HTTPException
import os
import pandas as pd
import numpy as np

from backend.engines.scoring_engine import ScoringEngine
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.importance_engine import ImportanceEngine
from backend.engines.completeness_engine import CompletenessEngine
from backend.services.correlation import (
    calculate_correlation_matrix,
    detect_strong_correlations
)
from backend.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

UPLOAD_DIR = "backend/storage/uploads"

# ✅ Helper function to clean NaN safely from any object
def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj


# ✅ NEW: Precise Cell-wise Outlier Percentage (IQR)
def calculate_outlier_percentage(df):
    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return 0.0

    total_cells = numeric_df.size
    outlier_cells = 0

    for col in numeric_df.columns:
        Q1 = numeric_df[col].quantile(0.25)
        Q3 = numeric_df[col].quantile(0.75)
        IQR = Q3 - Q1

        if IQR == 0:
            continue

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = numeric_df[
            (numeric_df[col] < lower_bound) |
            (numeric_df[col] > upper_bound)
        ][col]

        outlier_cells += outliers.count()

    return round((outlier_cells / total_cells) * 100, 2)


@router.get("/{dataset_id}")
def get_full_analytics(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # ================= CHANGED TO COUNTS =================
    missing_count = int(df.isnull().all(axis=1).sum())
    duplicate_count = int(df.duplicated(keep="first").sum())

    # ================= KEEP PERCENTAGE FOR SCORING =================
    missing_percentage = (missing_count / total_cells) * 100 if total_cells else 0
    duplicate_percentage = (duplicate_count / total_rows) * 100 if total_rows else 0

    # ✅ UPDATED: Using precise cell-wise IQR calculation
    outlier_pct = calculate_outlier_percentage(df)

    # ================= NOISY DATA (Cell-wise using Z-score) =================
    numeric_df = df.select_dtypes(include=["number"])

    if not numeric_df.empty:
        z_scores = np.abs((numeric_df - numeric_df.mean()) / numeric_df.std())
        noisy_cells = (z_scores > 3).sum().sum()
        total_numeric_cells = numeric_df.shape[0] * numeric_df.shape[1]
        noisy_percentage = (
            (noisy_cells / total_numeric_cells) * 100
            if total_numeric_cells > 0 else 0
        )
    else:
        noisy_percentage = 0

    quality_score = ScoringEngine.calculate_score(
        missing_percentage,
        duplicate_percentage,
        outlier_pct,
        noisy_percentage
    )

    completeness = CompletenessEngine.calculate(df)

    # Advanced Data Type Classification
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()
    boolean_columns = df.select_dtypes(include=["bool"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime"]).columns.tolist()

    importance = ImportanceEngine.calculate(df)

    column_outliers = OutlierEngine.detect_column_outliers(df, "iqr")

    correlation_matrix = calculate_correlation_matrix(df)
    strong_pairs = detect_strong_correlations(df)

    correlation_matrix = {
        k: {kk: float(vv) for kk, vv in v.items()}
        for k, v in correlation_matrix.items()
    }

    recommendations = RecommendationService.generate(df)

    # ================= ML READINESS =================
    if quality_score < 60:
        readiness = "Not Ready"
        badge_color = "red"
    elif quality_score < 75:
        readiness = "Needs Work"
        badge_color = "orange"
    elif quality_score < 90:
        readiness = "Good"
        badge_color = "blue"
    else:
        readiness = "ML Ready"
        badge_color = "green"

    # ================= SAFE JSON CLEANING =================
    df_clean = df.replace([np.inf, -np.inf], np.nan)
    preview_rows = df_clean.head(20).where(
        pd.notnull(df_clean), None
    ).to_dict(orient="records")

    # ================= RETURN RESPONSE =================
    response = {
        "profile": {
            "rows": total_rows,
            "columns": total_cols,
            "missing_count": missing_count,
            "duplicate_count": duplicate_count,
            "quality_score": round(quality_score, 2),
            "completeness": round(completeness, 2),
        },
        "ml_readiness": {
            "label": readiness,
            "color": badge_color
        },
        "data_types": {
            "numeric": numeric_columns,
            "categorical": categorical_columns,
            "boolean": boolean_columns,
            "datetime": datetime_columns,
        },
        "importance": importance,
        "outliers": {
            "overall_percentage": outlier_pct,
            "noisy_percentage": round(noisy_percentage, 2),
            "column_outliers": column_outliers,
        },
        "correlation": {
            "matrix": correlation_matrix,
            "strong_pairs": strong_pairs,
        },
        "ai_review": recommendations
    }

    return clean_nan(response)