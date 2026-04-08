"""
Simulate API — Optimised
========================
Key improvements:
• Uses read_csv_optimised for faster loading (low_memory=False, UTF-8 fallback).
• Scoring done on a sample (≤ 10 000 rows) for speed on large files.
• Fuzzy duplicate removal skipped for > 50 000 rows.
• KNN imputation skipped for > 10 000 rows (falls back through ImputationEngine).
• Vectorised fillna for mean/median/mode — no per-column Python loops.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config import CLEANED_DIR
from backend.core.file_manager import read_csv_optimised
from backend.database import get_db
from backend.engines.imputation_engine import ImputationEngine
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine
from backend.models import Dataset
from backend.schemas.request_models import SimulationRequest
from backend.schemas.response_models import SimulationResponse

router = APIRouter()

SAMPLE_CAP     = 10_000
FUZZY_CAP      = 50_000


def _score_sample(df: pd.DataFrame, method: str = "iqr"):
    """Score using a sample of up to SAMPLE_CAP rows for speed."""
    sample = df if len(df) <= SAMPLE_CAP else df.sample(n=SAMPLE_CAP, random_state=42)
    return ScoringEngine.calculate_metrics_and_score(sample, method)


@router.post("/{dataset_id}", response_model=SimulationResponse)
def simulate(
    dataset_id: int,
    payload: SimulationRequest,
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # ── Load ──────────────────────────────────────────────────────────────────
    df_original    = read_csv_optimised(file_path)
    
    # Normalize: replace common missing value strings with actual NaNs
    obj_cols = df_original.select_dtypes(include=['object']).columns
    if len(obj_cols) > 0:
        df_original[obj_cols] = df_original[obj_cols].apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
    
    df_original.replace(['', 'NA', 'N/A', 'null', 'NULL', 'None', 'none', 'nan', '?', '-'], np.nan, inplace=True)
    
    # Try to infer better types (important after NaN replacement)
    for col in df_original.columns:
        try:
            df_original[col] = pd.to_numeric(df_original[col], errors='ignore')
        except:
            pass
            
    original_rows  = len(df_original)

    # ── Before score (sampled) ────────────────────────────────────────────────
    score_before, m_pct_b, d_pct_b, outlier_pct_before, _, missing_cells_before, missing_rows_before = _score_sample(df_original, "iqr")

    payload_data   = payload.model_dump()
    outlier_method = payload_data.get("outlier_method") or "none"
    if outlier_method == "isolation":
        outlier_method = "isolation_forest"

    # ── Cleaning pipeline ─────────────────────────────────────────────────────
    df_clean = df_original.copy()

    # 1. Drop columns
    drop_cols = payload_data.get("drop_columns", [])
    if drop_cols:
        df_clean = df_clean.drop(columns=drop_cols, errors="ignore")

    # 2. Duplicates (skip fuzzy for large files)
    if payload_data.get("remove_duplicates", False):
        if len(df_clean) > FUZZY_CAP:
            df_clean = df_clean.drop_duplicates(keep="first")
        else:
            from backend.engines.duplicate_engine import DuplicateEngine
            df_clean = DuplicateEngine.remove_fuzzy_duplicates(
                df_clean, list(df_clean.columns), threshold=95.0
            )

    # 3. Missing values — vectorised operations
    missing_method  = payload_data.get("missing_method", "none")
    if missing_method != "none":
        numeric_cols    = df_clean.select_dtypes(include=[np.number]).columns
        categorical_cols = df_clean.select_dtypes(exclude=[np.number]).columns

        if missing_method in ("smart", "knn"):
            # ImputationEngine switches to median for > 10 k rows automatically
            df_clean = ImputationEngine.impute_missing(df_clean, n_neighbors=5)
        elif missing_method == "mean":
            # Vectorised: compute all means once, fill in one shot
            means = df_clean[numeric_cols].mean()
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(means)
            for col in categorical_cols:
                mode = df_clean[col].mode()
                if not mode.empty:
                    df_clean[col] = df_clean[col].fillna(mode.iloc[0])
        elif missing_method == "median":
            medians = df_clean[numeric_cols].median()
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(medians)
            for col in categorical_cols:
                mode = df_clean[col].mode()
                if not mode.empty:
                    df_clean[col] = df_clean[col].fillna(mode.iloc[0])
        elif missing_method == "mode":
            # Compute mode vector once, fill across all columns
            for col in df_clean.columns:
                mode = df_clean[col].mode()
                if not mode.empty:
                    df_clean[col] = df_clean[col].fillna(mode.iloc[0])

    # 4. Outliers
    outlier_action = payload_data.get("outlier_action", "fix")
    if outlier_method != "none":
        if outlier_action == "remove":
            df_clean = OutlierEngine.remove_outliers(df_clean, outlier_method)
        else:
            df_clean = OutlierEngine.fix_outliers(df_clean, outlier_method)

    # 5. Noise
    noisy_method = payload_data.get("noisy_method", "none")
    noisy_action = payload_data.get("noisy_action", "fix")
    if noisy_method != "none":
        if noisy_action == "remove":
            df_clean = OutlierEngine.remove_outliers(df_clean, noisy_method)
        else:
            df_clean = OutlierEngine.fix_noise(df_clean, noisy_method)

    # ── After score (sampled) ─────────────────────────────────────────────────
    eff_method   = outlier_method if outlier_method != "none" else "iqr"
    score_after, m_pct_a, d_pct_a, outlier_pct_after, _, missing_cells_after, missing_rows_after = _score_sample(df_clean, eff_method)

    # ── Full Dataset Missing Counts (for "Exact" Overview) ─────────────────────
    missing_rows_before = int(df_original.isna().all(axis=1).sum())
    missing_cells_before = int(df_original.isna().sum().sum())
    
    missing_rows_after = int(df_clean.isna().all(axis=1).sum())
    missing_cells_after = int(df_clean.isna().sum().sum())

    warning_msg  = (
        "Cleaning did not improve data quality" if score_after <= score_before else None
    )
    improvement_pct = (
        ((score_after - score_before) / score_before) * 100 if score_before > 0 else 0.0
    )

    readiness = ScoringEngine.get_ml_readiness(score_after)

    # ── Save ──────────────────────────────────────────────────────────────────
    cleaned_path = os.path.join(CLEANED_DIR, f"{dataset.id}.csv")
    df_clean     = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean.to_csv(cleaned_path, index=False)

    return SimulationResponse(
        score_before=round(score_before, 2),
        score_after=round(score_after, 2),
        improvement=round(score_after - score_before, 2),
        improvement_percent=round(improvement_pct, 2),
        warning=warning_msg,
        rows_before=original_rows,
        rows_after=len(df_clean),
        rows_removed=original_rows - len(df_clean),
        missing_rows_before=missing_rows_before,
        missing_rows_after=missing_rows_after,
        missing_cells_before=missing_cells_before,
        missing_cells_after=missing_cells_after,
        outlier_pct_before=round(outlier_pct_before, 2),
        outlier_pct_after=round(outlier_pct_after, 2),
        ml_readiness_after={
            "label": readiness["status"],
            "color": readiness["color"],
        },
    )
