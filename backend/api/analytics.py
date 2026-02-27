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
    generate_heatmap_data,
    detect_strong_correlations
)
from backend.services.recommendation_service import RecommendationService


router = APIRouter(prefix="/analytics", tags=["Analytics"])

# ✅ FIXED DIRECTORY (must match upload.py)
UPLOAD_DIR = "backend/storage/uploads"


@router.get("/{dataset_id}")
def get_full_analytics(dataset_id: str):

    # ================= FILE PATH =================
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    # ================= LOAD DATA =================
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read dataset: {str(e)}")

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # ================= BASIC METRICS =================
    missing_pct = (
        (df.isnull().sum().sum() / total_cells) * 100
        if total_cells > 0 else 0
    )

    duplicate_pct = (
        (df.duplicated().sum() / total_rows) * 100
        if total_rows > 0 else 0
    )

    outlier_pct = OutlierEngine.detect_percentage(df, "iqr")

    quality_score = ScoringEngine.calculate_score(
        missing_pct,
        duplicate_pct,
        outlier_pct
    )

    completeness = CompletenessEngine.calculate(df)

    # ================= IMPORTANCE =================
    importance = ImportanceEngine.calculate(df)

    # ================= OUTLIERS =================
    column_outliers = OutlierEngine.detect_column_outliers(df, "iqr")
    outlier_chart = OutlierEngine.generate_outlier_chart_data(df, "iqr")

    # ================= CORRELATION =================
    correlation_matrix = calculate_correlation_matrix(df)
    heatmap_data = generate_heatmap_data(df)
    strong_pairs = detect_strong_correlations(df)

    # ================= RECOMMENDATIONS =================
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
    preview_rows = df_clean.head(20).where(pd.notnull(df_clean), None).to_dict(orient="records")

    # ================= RETURN RESPONSE =================
    return {
        "profile": {
            "rows": total_rows,
            "columns": total_cols,
            "missing_percentage": round(missing_pct, 2),
            "duplicate_percentage": round(duplicate_pct, 2),
            "quality_score": quality_score,
            "completeness": round(completeness, 2),
        },
        "importance": importance,
        "outliers": {
            "overall_percentage": outlier_pct,
            "column_outliers": column_outliers,
            "chart_data": outlier_chart,
        },
        "correlation": {
            "matrix": correlation_matrix,
            "heatmap": heatmap_data,
            "strong_pairs": strong_pairs,
        },
        "recommendations": recommendations,
        "ml_readiness": {
            "label": readiness,
            "color": badge_color,
        },
        "preview": preview_rows
    }