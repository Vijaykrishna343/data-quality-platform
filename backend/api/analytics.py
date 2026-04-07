"""
Analytics API — Optimised with Result Caching
=============================================
• Checks DB for an existing AnalysisResult before recomputing.
• Uses a sampled DataFrame for heavy analytics (scoring, outliers, correlation).
• Forces IQR method throughout — fastest deterministic outlier algorithm.
• All heavy AI-style ML calls (Isolation Forest, LOF) are now sample-bound.
• Cache invalidation: append ?invalidate_cache=true to force a recompute.
"""
from __future__ import annotations

import json
import logging
import os

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.engines.completeness_engine import CompletenessEngine
from backend.engines.importance_engine import ImportanceEngine
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine
from backend.models import AnalysisResult, Dataset
from backend.services.correlation import (
    calculate_correlation_matrix,
    detect_strong_correlations,
)
from backend.services.recommendation_service import RecommendationService
from backend.core.file_manager import read_csv_optimised

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)

# ─── Utility ──────────────────────────────────────────────────────────────────

def _clean_nan(obj):
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(i) for i in obj]
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj


def _classify_columns(df: pd.DataFrame):
    numeric_cols   = df.select_dtypes(include=["number"]).columns.tolist()
    boolean_cols   = df.select_dtypes(include=["bool"]).columns.tolist()
    datetime_cols  = df.select_dtypes(include=["datetime"]).columns.tolist()
    raw_cat        = df.select_dtypes(include=["object"]).columns.tolist()
    categorical, alphanumeric = [], []
    for col in raw_cat:
        s = df[col].astype(str)
        if (s.str.contains(r"[a-zA-Z]") & s.str.contains(r"[0-9]")).any():
            alphanumeric.append(col)
        else:
            categorical.append(col)
    return numeric_cols, categorical, alphanumeric, boolean_cols, datetime_cols


# ─── Route ────────────────────────────────────────────────────────────────────

@router.get("/{dataset_id}")
def get_full_analytics(
    dataset_id: int,
    invalidate_cache: bool = Query(False),
    db: Session = Depends(get_db),
):
    # ── 1. Load Dataset Row ─────────────────────────────────────────────────
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # ── 2. Cache Lookup ─────────────────────────────────────────────────────
    if not invalidate_cache:
        cached = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.dataset_id == dataset_id)
            .order_by(AnalysisResult.id.desc())
            .first()
        )
        if cached and cached.result:
            logger.info(f"Cache HIT — dataset_id={dataset_id}")
            return cached.result          # ← skip all computation

    logger.info(f"Cache MISS — computing analytics for dataset_id={dataset_id}")

    # ── 3. Auto-clean on first visit ────────────────────────────────────────
    meta_path       = file_path.replace(".csv", "_meta.json")
    auto_clean_report: dict = {}

    if os.path.exists(meta_path):
        with open(meta_path) as f:
            auto_clean_report = json.load(f)
        df = read_csv_optimised(file_path)
    else:
        df              = read_csv_optimised(file_path)
        initial_rows    = len(df)
        df              = df.drop_duplicates(keep="first")
        dups_removed    = initial_rows - len(df)
        auto_clean_report = {"duplicates_removed": dups_removed}
        df.to_csv(file_path, index=False)
        with open(meta_path, "w") as f:
            json.dump(auto_clean_report, f)

    total_rows = len(df)
    total_cols = len(df.columns)

    # ── 4. Sample for heavy analytics ───────────────────────────────────────
    SAMPLE_CAP = 10_000
    df_s = df.sample(n=min(SAMPLE_CAP, total_rows), random_state=42)

    try:
        logger.info(f"Analytics start — dataset={dataset_id} rows={total_rows}")

        # Scoring (sampled)
        quality_score, m_pct, d_pct, o_pct, n_pct = (
            ScoringEngine.calculate_metrics_and_score(df_s, "iqr")
        )

        # Full-DF simple counts
        missing_count   = int(df.isnull().any(axis=1).sum())
        duplicate_count = int(df.duplicated(keep="first").sum())

        # Completeness & Importance (sampled)
        completeness    = CompletenessEngine.calculate(df_s)
        importance      = ImportanceEngine.calculate(df_s)

        # Outliers per column (sampled, IQR only — fastest)
        column_outliers = OutlierEngine.detect_column_outliers(df_s, "iqr")

        # Column classification (full df for correctness)
        (numeric_cols, categorical_cols,
         alphanumeric_cols, boolean_cols, datetime_cols) = _classify_columns(df)

        # Correlation (sampled)
        corr_matrix  = calculate_correlation_matrix(df_s)
        strong_pairs = detect_strong_correlations(df_s)
        corr_clean   = {
            k: {kk: float(vv) for kk, vv in v.items()}
            for k, v in corr_matrix.items()
        }

        recommendations = RecommendationService.generate(df_s)
        readiness       = ScoringEngine.get_ml_readiness(quality_score)

        response = {
            "profile": {
                "rows":            total_rows,
                "columns":         total_cols,
                "missing_count":   missing_count,
                "duplicate_count": duplicate_count,
                "quality_score":   round(quality_score, 2),
                "completeness":    round(completeness, 2),
            },
            "ml_readiness": {
                "label": readiness["status"],
                "color": readiness["color"],
            },
            "data_types": {
                "numeric":      numeric_cols,
                "categorical":  categorical_cols,
                "alphanumeric": alphanumeric_cols,
                "boolean":      boolean_cols,
                "datetime":     datetime_cols,
            },
            "importance":   importance,
            "outliers": {
                "overall_percentage": round(o_pct, 2),
                "noisy_percentage":   round(n_pct, 2),
                "column_outliers":    column_outliers,
                "breakdown":          ScoringEngine.score_breakdown(m_pct, d_pct, o_pct, n_pct),
            },
            "correlation": {
                "matrix":       corr_clean,
                "strong_pairs": strong_pairs,
            },
            "auto_clean_report": auto_clean_report,
            "ai_review":         recommendations,
        }

    except Exception as exc:
        logger.error(f"Analytics failed dataset={dataset_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analytical profiling failed: {exc}")

    # ── 5. Persist & Return ─────────────────────────────────────────────────
    cleaned = _clean_nan(response)
    db.add(AnalysisResult(dataset_id=dataset_id, result=cleaned))
    db.commit()

    return cleaned