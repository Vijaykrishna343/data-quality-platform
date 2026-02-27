from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import numpy as np

from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine
from backend.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/simulate", tags=["Simulation"])

UPLOAD_DIR = "backend/uploads"
CLEAN_DIR = "backend/storage/cleaned"
os.makedirs(CLEAN_DIR, exist_ok=True)


@router.post("/{dataset_id}")
def simulate(dataset_id: str, payload: dict):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    total_rows = len(df)
    total_cells = df.shape[0] * df.shape[1]

    missing_pct = (df.isnull().sum().sum() / total_cells) * 100 if total_cells else 0
    duplicate_pct = (df.duplicated().sum() / total_rows) * 100 if total_rows else 0
    outlier_pct = OutlierEngine.detect_percentage(df, payload.get("outlier_method", "iqr"))

    score_before = ScoringEngine.calculate_score(
        df, missing_pct, duplicate_pct, outlier_pct
    )

    df_cleaned = df.copy()

    if payload.get("handle_missing"):
        df_cleaned = df_cleaned.fillna(df_cleaned.median(numeric_only=True))

    if payload.get("remove_duplicates"):
        df_cleaned = df_cleaned.drop_duplicates()

    if payload.get("outlier_method"):
        df_cleaned = OutlierEngine.remove_outliers(
            df_cleaned, payload.get("outlier_method")
        )

    df_cleaned = df_cleaned.replace({np.nan: None})

    total_rows_after = len(df_cleaned)
    total_cells_after = df_cleaned.shape[0] * df_cleaned.shape[1]

    missing_pct_after = (
        (df_cleaned.isnull().sum().sum() / total_cells_after) * 100
        if total_cells_after else 0
    )

    duplicate_pct_after = (
        (df_cleaned.duplicated().sum() / total_rows_after) * 100
        if total_rows_after else 0
    )

    outlier_pct_after = OutlierEngine.detect_percentage(
        df_cleaned, payload.get("outlier_method", "iqr")
    )

    score_after = ScoringEngine.calculate_score(
        df_cleaned, missing_pct_after, duplicate_pct_after, outlier_pct_after
    )

    cleaned_path = os.path.join(CLEAN_DIR, f"{dataset_id}.csv")
    df_cleaned.to_csv(cleaned_path, index=False)

    return {
        "score_before": round(score_before, 2),
        "score_after": round(score_after, 2),
        "improvement": round(score_after - score_before, 2),
        "rows_after": total_rows_after
    }