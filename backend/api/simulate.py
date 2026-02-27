from fastapi import APIRouter, HTTPException
import os
import pandas as pd
import numpy as np

from backend.engines.scoring_engine import ScoringEngine
from backend.engines.outlier_engine import OutlierEngine

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"
CLEAN_DIR = "backend/storage/cleaned"

os.makedirs(CLEAN_DIR, exist_ok=True)


@router.post("/{dataset_id}")
def simulate(dataset_id: str, payload: dict):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)
    original_rows = len(df)

    # ================= DROP COLUMNS =================
    drop_cols = payload.get("drop_columns", [])
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    # ================= BEFORE METRICS =================
    total_cells = len(df) * len(df.columns)

    missing_pct = (
        (df.isnull().sum().sum() / total_cells) * 100
        if total_cells > 0 else 0
    )

    duplicate_pct = (
        (df.duplicated().sum() / len(df)) * 100
        if len(df) > 0 else 0
    )

    outlier_pct = OutlierEngine.detect_percentage(
        df,
        payload.get("outlier_method", "iqr")
    )

    score_before = ScoringEngine.calculate_score(
        missing_pct,
        duplicate_pct,
        outlier_pct
    )

    # ================= APPLY CLEANING =================
    df_clean = df.copy()

    if payload.get("handle_missing"):
        df_clean = df_clean.fillna(df_clean.median(numeric_only=True))

    if payload.get("remove_duplicates"):
        df_clean = df_clean.drop_duplicates()

    if payload.get("outlier_method") and payload.get("outlier_method") != "none":
        df_clean = OutlierEngine.remove_outliers(
            df_clean,
            payload.get("outlier_method")
        )

    # ================= AFTER METRICS =================
    total_cells_after = len(df_clean) * len(df_clean.columns)

    missing_pct_after = (
        (df_clean.isnull().sum().sum() / total_cells_after) * 100
        if total_cells_after > 0 else 0
    )

    duplicate_pct_after = (
        (df_clean.duplicated().sum() / len(df_clean)) * 100
        if len(df_clean) > 0 else 0
    )

    outlier_pct_after = OutlierEngine.detect_percentage(
        df_clean,
        payload.get("outlier_method", "iqr")
    )

    score_after = ScoringEngine.calculate_score(
        missing_pct_after,
        duplicate_pct_after,
        outlier_pct_after
    )

    # ================= SAVE CLEANED FILE (SAFE) =================
    cleaned_path = os.path.join(CLEAN_DIR, f"{dataset_id}.csv")

    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean.to_csv(cleaned_path, index=False)

    return {
        "score_before": round(score_before, 2),
        "score_after": round(score_after, 2),
        "improvement": round(score_after - score_before, 2),
        "rows_before": original_rows,
        "rows_after": len(df_clean),
    }