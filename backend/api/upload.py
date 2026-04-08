"""
Upload API — Optimised
======================
• Streams file in 1 MB chunks (fast disk write, no full in-memory load).
• Fast row-count via newline streaming (avoids full pandas parse).
• Validates CSV with just the header + 5 preview rows.
• Large files (≥ LARGE_FILE_THRESHOLD_MB) are handled asynchronously:
    → returns task_id immediately
    → background thread runs cleaning + analytics
    → frontend polls /upload/status/{task_id}
• Small files are handled synchronously as before.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import uuid

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.api.tasks import (
    STAGE_MESSAGES,
    create_task,
    fail_task,
    get_task,
    set_dataset_id,
    update_task,
)
from backend.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
from backend.core.file_manager import fast_row_count, read_csv_optimised
from backend.database import SessionLocal, get_db
from backend.models import Dataset
from backend.schemas.response_models import UploadResponse

router = APIRouter()
logger = logging.getLogger(__name__)

LARGE_FILE_THRESHOLD_MB = 5  # files above this go async
CHUNK_SIZE = 1024 * 1024     # 1 MB write chunks


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _save_file(file_obj, file_path: str) -> int:
    """Stream-write uploaded bytes; return total bytes written."""
    size = 0
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    with open(file_path, "wb") as f:
        while True:
            chunk = file_obj.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit",
                )
            f.write(chunk)
    return size


async def _async_save_file(file_obj, file_path: str) -> int:
    """Async version of _save_file for FastAPI async endpoints."""
    size = 0
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    with open(file_path, "wb") as f:
        while True:
            chunk = await file_obj.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit",
                )
            f.write(chunk)
    return size


def _persist_dataset(filename: str, file_path: str, db: Session) -> Dataset:
    ds = Dataset(name=filename, file_path=file_path)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


# ─── Background Processing ───────────────────────────────────────────────────

def _run_background_pipeline(task_id: str, file_path: str, filename: str):
    """
    Full pipeline executed in a background thread for large files.
    Stages: reading → cleaning → scoring → analytics → completed
    """
    db: Session = SessionLocal()
    try:
        # ── Stage: reading ──────────────────────────────────────────────
        update_task(task_id, "reading")
        df = read_csv_optimised(file_path)

        # ── Persist dataset to DB ───────────────────────────────────────
        ds = _persist_dataset(filename, file_path, db)
        set_dataset_id(task_id, ds.id)

        # ── Stage: cleaning ─────────────────────────────────────────────
        update_task(task_id, "cleaning")
        initial_rows = len(df)
        df = df.drop_duplicates(keep="first")
        duplicates_removed = initial_rows - len(df)
        df.to_csv(file_path, index=False)

        meta_path = file_path.replace(".csv", "_meta.json")
        with open(meta_path, "w") as f:
            json.dump({"duplicates_removed": duplicates_removed}, f)

        # ── Stage: scoring ──────────────────────────────────────────────
        update_task(task_id, "scoring")
        from backend.engines.scoring_engine import ScoringEngine
        df_sample = df.sample(n=min(10_000, len(df)), random_state=42)
        (quality_score, m_pct, d_pct, o_pct, n_pct, m_cells, m_rows) = (
            ScoringEngine.calculate_metrics_and_score(df_sample, "iqr")
        )

        # ── Stage: analytics ────────────────────────────────────────────
        update_task(task_id, "analytics")
        from backend.engines.completeness_engine import CompletenessEngine
        from backend.engines.importance_engine import ImportanceEngine
        from backend.engines.outlier_engine import OutlierEngine
        from backend.services.correlation import (
            calculate_correlation_matrix,
            detect_strong_correlations,
        )
        from backend.services.recommendation_service import RecommendationService

        completeness    = CompletenessEngine.calculate(df_sample)
        importance      = ImportanceEngine.calculate(df_sample)
        column_outliers = OutlierEngine.detect_column_outliers(df_sample, "iqr")
        corr_matrix     = calculate_correlation_matrix(df_sample)
        strong_pairs    = detect_strong_correlations(df_sample)
        recommendations = RecommendationService.generate(df_sample)
        readiness       = ScoringEngine.get_ml_readiness(quality_score)

        numeric_cols      = df.select_dtypes(include=["number"]).columns.tolist()
        boolean_cols      = df.select_dtypes(include=["bool"]).columns.tolist()
        datetime_cols     = df.select_dtypes(include=["datetime"]).columns.tolist()
        raw_cat           = df.select_dtypes(include=["object"]).columns.tolist()
        categorical_cols, alphanumeric_cols = [], []
        for col in raw_cat:
            s = df[col].astype(str)
            if (s.str.contains(r"[a-zA-Z]") & s.str.contains(r"[0-9]")).any():
                alphanumeric_cols.append(col)
            else:
                categorical_cols.append(col)

        corr_matrix_clean = {
            k: {kk: float(vv) for kk, vv in v.items()}
            for k, v in corr_matrix.items()
        }

        import numpy as np

        def _clean_nan(obj):
            if isinstance(obj, dict):
                return {k: _clean_nan(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_clean_nan(i) for i in obj]
            if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            return obj

        df_clean_na = df.replace(r'^\s*$', np.nan, regex=True)
        result = _clean_nan({
            "profile": {
                "rows":           len(df),
                "columns":        len(df.columns),
                "missing_rows":   int(df_clean_na.isnull().all(axis=1).sum()),
                "missing_cells":  int(df_clean_na.isnull().sum().sum()),
                "duplicate_count": int(df.duplicated(keep="first").sum()),
                "quality_score":  round(quality_score, 2),
                "completeness":   round(completeness, 2),
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
            "importance":        importance,
            "outliers": {
                "overall_percentage": round(o_pct, 2),
                "noisy_percentage":   round(n_pct, 2),
                "column_outliers":    column_outliers,
                "breakdown":          ScoringEngine.score_breakdown(m_pct, d_pct, o_pct, n_pct),
            },
            "correlation": {
                "matrix":       corr_matrix_clean,
                "strong_pairs": strong_pairs,
            },
            "auto_clean_report": {"duplicates_removed": duplicates_removed},
            "ai_review":         recommendations,
        })

        # ── Persist result ──────────────────────────────────────────────
        from backend.models import AnalysisResult
        ar = AnalysisResult(dataset_id=ds.id, result=result)
        db.add(ar)
        db.commit()

        # ── Stage: completed ────────────────────────────────────────────
        update_task(task_id, "completed", result={"dataset_id": ds.id, "analytics": result})
        logger.info(f"Background pipeline complete — task={task_id} dataset={ds.id}")

    except Exception as exc:
        logger.error(f"Background pipeline failed task={task_id}: {exc}", exc_info=True)
        fail_task(task_id, str(exc))
        if os.path.exists(file_path):
            os.remove(file_path)
    finally:
        db.close()


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file.

    • Small files  (< LARGE_FILE_THRESHOLD_MB) → synchronous, returns dataset_id.
    • Large files  (≥ LARGE_FILE_THRESHOLD_MB) → async, returns task_id immediately.
    """
    file_path: str | None = None
    try:
        filename  = file.filename or "dataset.csv"
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        file_id   = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")

        # Stream-write
        file_size_bytes = await _async_save_file(file, file_path)
        file_size_mb    = file_size_bytes / (1024 * 1024)

        # Validate structure with just 5 rows
        try:
            df_peek = read_csv_optimised(file_path, nrows=5)
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {e}")
        if df_peek.empty:
            raise ValueError("CSV file is empty or has no data rows")

        # ── LARGE FILE → async ──────────────────────────────────────────
        if file_size_mb >= LARGE_FILE_THRESHOLD_MB:
            task_id = create_task(dataset_id=None)
            thread  = threading.Thread(
                target=_run_background_pipeline,
                args=(task_id, file_path, filename),
                daemon=True,
            )
            thread.start()
            logger.info(
                f"Large file ({file_size_mb:.1f} MB) — async processing task={task_id}"
            )
            return {
                "mode":      "async",
                "task_id":   task_id,
                "filename":  filename,
                "size_mb":   round(file_size_mb, 2),
                "message":   "Large file detected. Processing in background. Poll /upload/status/{task_id}",
                "stages":    list(STAGE_MESSAGES.values()),
            }

        # ── SMALL FILE → sync ───────────────────────────────────────────
        ds = _persist_dataset(filename, file_path, db)
        logger.info(f"Small file uploaded — dataset_id={ds.id}")
        return UploadResponse(
            dataset_id=ds.id,
            filename=filename,
            message="File uploaded successfully",
        )

    except HTTPException:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as exc:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Upload error: {exc}")
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {exc}")
    finally:
        await file.close()


@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """Poll this endpoint every 2 s to track async upload progress."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
