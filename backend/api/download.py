from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import pandas as pd
import numpy as np

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"
CLEAN_DIR = "backend/storage/cleaned"

os.makedirs(CLEAN_DIR, exist_ok=True)


# =====================================================
# DATASET PREVIEW (JSON SAFE + PAGINATION SAFE)
# =====================================================
@router.get("/preview/{dataset_id}")
def preview_dataset(dataset_id: str, page: int = 1, page_size: int = 20):

    cleaned_path = os.path.join(CLEAN_DIR, f"{dataset_id}.csv")
    original_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    # Priority: cleaned file first
    if os.path.exists(cleaned_path):
        file_path = cleaned_path
    elif os.path.exists(original_path):
        file_path = original_path
    else:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")

    total_rows = len(df)

    # If empty dataset
    if total_rows == 0:
        return {
            "columns": [],
            "rows": [],
            "total_rows": 0
        }

    # ---------------------------
    # Safe Pagination
    # ---------------------------
    page = max(page, 1)
    page_size = max(page_size, 1)

    start = (page - 1) * page_size
    end = start + page_size

    if start >= total_rows:
        start = 0
        end = page_size

    page_df = df.iloc[start:end]

    # ---------------------------
    # CRITICAL: JSON SAFE CLEANING
    # ---------------------------
    page_df = page_df.replace([np.inf, -np.inf], None)
    page_df = page_df.astype(object)

    records = []
    for _, row in page_df.iterrows():
        clean_row = {}
        for col, val in row.items():
            if pd.isna(val):
                clean_row[col] = None
            else:
                clean_row[col] = val
        records.append(clean_row)

    return {
        "columns": list(page_df.columns),
        "rows": records,
        "total_rows": total_rows
    }


# =====================================================
# DOWNLOAD CLEANED DATASET
# =====================================================
@router.get("/{dataset_id}")
def download_cleaned(dataset_id: str):

    cleaned_path = os.path.join(CLEAN_DIR, f"{dataset_id}.csv")

    if not os.path.exists(cleaned_path):
        raise HTTPException(status_code=404, detail="Cleaned dataset not found")

    return FileResponse(
        cleaned_path,
        media_type="text/csv",
        filename=f"{dataset_id}_cleaned.csv"
    )