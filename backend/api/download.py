"""
Download API — Optimised
========================
• Preview uses fast_row_count (newline streaming) instead of loading any data.
• Partial read with skiprows + nrows — never loads the full file for a page.
• Clean JSON fallback with NaN/Inf handling.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import CLEANED_DIR
from backend.core.file_manager import fast_row_count, read_csv
from backend.database import get_db
from backend.models import Dataset
from backend.schemas.response_models import PreviewResponse

router = APIRouter()


# ─── Preview ──────────────────────────────────────────────────────────────────

@router.get("/preview/{dataset_id}", response_model=PreviewResponse)
def preview_dataset(
    dataset_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    original_path = dataset.file_path
    cleaned_path  = os.path.join(CLEANED_DIR, f"{dataset.id}.csv")

    # Priority: cleaned file first
    file_path = (
        cleaned_path if os.path.exists(cleaned_path)
        else original_path if os.path.exists(original_path)
        else None
    )
    if not file_path:
        raise HTTPException(status_code=404, detail="Dataset file not found")

    # ── Fast row count via newline streaming (~10× faster than pd.read_csv) ──
    total_rows = fast_row_count(file_path)
    if total_rows <= 0:
        # Fallback: read one column
        try:
            idx = pd.read_csv(file_path, usecols=[0])
            total_rows = len(idx)
            del idx
        except Exception:
            total_rows = 0

    if total_rows == 0:
        return {"columns": [], "rows": [], "total_rows": 0}

    # ── Pagination ────────────────────────────────────────────────────────────
    page      = max(page, 1)
    page_size = max(page_size, 1)
    start     = (page - 1) * page_size
    if start >= total_rows:
        start = 0

    try:
        if start == 0:
            page_df = pd.read_csv(file_path, nrows=page_size)
        else:
            page_df = pd.read_csv(
                file_path, skiprows=range(1, start + 1), nrows=page_size
            )
    except Exception:
        # Final fallback
        df_all  = read_csv(file_path)
        page_df = df_all.iloc[start : start + page_size]

    # JSON-safe cleaning
    page_df = page_df.replace([np.inf, -np.inf], np.nan)
    page_df = page_df.where(pd.notnull(page_df), None)

    return {
        "columns":    list(page_df.columns),
        "rows":       page_df.to_dict(orient="records"),
        "total_rows": total_rows,
    }


# ─── Download ─────────────────────────────────────────────────────────────────

@router.get("/{dataset_id}")
def download_cleaned(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    cleaned_path = os.path.join(CLEANED_DIR, f"{dataset.id}.csv")
    if not os.path.exists(cleaned_path):
        raise HTTPException(status_code=404, detail="Cleaned dataset not found")

    return FileResponse(
        cleaned_path,
        media_type="text/csv",
        filename=f"{dataset_id}_cleaned.csv",
    )
