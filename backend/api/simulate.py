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

    # ================= LOAD ORIGINAL =================
    df_original = pd.read_csv(file_path)
    original_rows = len(df_original)

    # ================= BEFORE METRICS =================
    total_cells = len(df_original) * len(df_original.columns)

    missing_pct = (
        (df_original.isnull().sum().sum() / total_cells) * 100
        if total_cells > 0 else 0
    )

    duplicate_pct = (
        (df_original.duplicated().sum() / len(df_original)) * 100
        if len(df_original) > 0 else 0
    )

    outlier_pct = OutlierEngine.detect_percentage(
        df_original,
        payload.get("outlier_method", "iqr")
    )

    score_before = ScoringEngine.calculate_score(
        missing_pct,
        duplicate_pct,
        outlier_pct
    )

    # ================= START CLEANING =================
    df_clean = df_original.copy()

    drop_cols = payload.get("drop_columns", [])
    if drop_cols:
        df_clean = df_clean.drop(columns=drop_cols, errors="ignore")

    if payload.get("handle_missing"):
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(
            df_clean[numeric_cols].median()
        )

        categorical_cols = df_clean.select_dtypes(exclude=[np.number]).columns
        for col in categorical_cols:
            if df_clean[col].isnull().any():
                mode_series = df_clean[col].mode()
                df_clean[col] = df_clean[col].fillna(
                    mode_series.iloc[0] if not mode_series.empty else "Unknown"
                )

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

    # ================= ML READINESS AFTER =================
    if score_after < 60:
        readiness = {"label": "Not Ready", "color": "red"}
    elif score_after < 75:
        readiness = {"label": "Needs Work", "color": "orange"}
    elif score_after < 90:
        readiness = {"label": "Good", "color": "blue"}
    else:
        readiness = {"label": "ML Ready", "color": "green"}

    # ================= SAVE CLEANED FILE =================
    cleaned_path = os.path.join(CLEAN_DIR, f"{dataset_id}.csv")
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean.to_csv(cleaned_path, index=False)

    return {
        "score_before": round(score_before, 2),
        "score_after": round(score_after, 2),
        "improvement": round(score_after - score_before, 2),
        "rows_before": original_rows,
        "rows_after": len(df_clean),
        "rows_removed": original_rows - len(df_clean),
        "ml_readiness_after": readiness
    }