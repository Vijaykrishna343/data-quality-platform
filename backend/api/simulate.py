from fastapi import APIRouter, HTTPException, Depends
import os
import pandas as pd
import numpy as np

from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Dataset

from backend.core.file_manager import read_csv
from backend.engines.scoring_engine import ScoringEngine
from backend.engines.outlier_engine import OutlierEngine

router = APIRouter()

CLEAN_DIR = "backend/storage/cleaned"
os.makedirs(CLEAN_DIR, exist_ok=True)


@router.post("/{dataset_id}")
def simulate(dataset_id: int, payload: dict, db: Session = Depends(get_db)):

    # ✅ GET DATASET FROM DB
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # ================= LOAD ORIGINAL =================
    df_original = read_csv(file_path)
    original_rows = len(df_original)

    # ================= BEFORE METRICS =================
    score_before, missing_pct, duplicate_pct, outlier_pct, noisy_pct = ScoringEngine.calculate_metrics_and_score(
        df_original, "iqr"
    )

    # ================= START CLEANING =================
    df_clean = df_original.copy()

    # 1. Drop columns
    drop_cols = payload.get("drop_columns", [])
    if drop_cols:
        df_clean = df_clean.drop(columns=drop_cols, errors="ignore")

    # 2. Missing values
    missing_method = payload.get("missing_method", "none")
    if missing_method != "none":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        categorical_cols = df_clean.select_dtypes(exclude=[np.number]).columns

        if missing_method == "smart":
            if not numeric_cols.empty:
                df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
            for col in categorical_cols:
                mode_val = df_clean[col].mode()
                if not mode_val.empty:
                    df_clean[col] = df_clean[col].fillna(mode_val.iloc[0])
        else:
            if missing_method == "mean":
                df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
            elif missing_method == "median":
                df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
            elif missing_method == "mode":
                for col in df_clean.columns:
                    mode_val = df_clean[col].mode()
                    if not mode_val.empty:
                        df_clean[col] = df_clean[col].fillna(mode_val.iloc[0])

    # 3. Outliers
    outlier_method = payload.get("outlier_method", "none")
    outlier_action = payload.get("outlier_action", "fix")

    if outlier_method != "none":
        if outlier_action == "remove":
            df_clean = OutlierEngine.remove_outliers(df_clean, outlier_method)
        else:
            df_clean = OutlierEngine.fix_outliers(df_clean, outlier_method)

    # 4. Noise
    noisy_method = payload.get("noisy_method", "none")
    noisy_action = payload.get("noisy_action", "fix")

    if noisy_method != "none":
        if noisy_action == "remove":
            df_clean = OutlierEngine.remove_outliers(df_clean, noisy_method)
        else:
            df_clean = OutlierEngine.fix_noise(df_clean, noisy_method)

    # ================= AFTER METRICS =================
    score_after, _, _, _, _ = ScoringEngine.calculate_metrics_and_score(
        df_clean, payload.get("outlier_method", "iqr")
    )

    readiness = ScoringEngine.get_ml_readiness(score_after)

    # ================= SAVE CLEANED FILE =================
    cleaned_path = os.path.join(CLEAN_DIR, f"{dataset_id}.csv")
    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean.to_csv(cleaned_path, index=False)

    # ================= RESPONSE =================
    return {
        "score_before": round(score_before, 2),
        "score_after": round(score_after, 2),
        "improvement": round(score_after - score_before, 2),
        "rows_before": original_rows,
        "rows_after": len(df_clean),
        "rows_removed": original_rows - len(df_clean),
        "ml_readiness_after": {
            "label": readiness["status"],
            "color": readiness["color"]
        }
    }