from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import pandas as pd
import numpy as np

from backend.core.file_manager import read_csv
from backend.config import CLEANED_DIR
from backend.database import get_db
from backend.models import Dataset
from backend.schemas.response_models import PreviewResponse
from sqlalchemy.orm import Session

router = APIRouter()

# =====================================================
# DATASET PREVIEW (JSON SAFE + FAST + PAGINATION SAFE)
# =====================================================

@router.get("/preview/{dataset_id}", response_model=PreviewResponse)
def preview_dataset(dataset_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    # Get dataset from database
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    original_file_path = dataset.file_path
    cleaned_path = os.path.join(CLEANED_DIR, f"{dataset.id}.csv")

    # Priority: cleaned first
    if os.path.exists(cleaned_path):
        file_path = cleaned_path
    elif os.path.exists(original_file_path):
        file_path = original_file_path
    else:
        raise HTTPException(status_code=404, detail="Dataset file not found")

    try:
        df = read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset: {str(e)}")

    total_rows = len(df)

    if total_rows == 0:
        return {
            "columns": [],
            "rows": [],
            "total_rows": 0
        }

    # Safe pagination
    page = max(page, 1)
    page_size = max(page_size, 1)

    start = (page - 1) * page_size
    end = start + page_size

    if start >= total_rows:
        start = 0
        end = page_size

    page_df = df.iloc[start:end]

    # =====================================================
    # ENTERPRISE SAFE JSON CLEANING
    # =====================================================

    page_df = page_df.replace([np.inf, -np.inf], np.nan)
    page_df = page_df.where(pd.notnull(page_df), None)

    return {
        "columns": list(page_df.columns),
        "rows": page_df.to_dict(orient="records"),
        "total_rows": total_rows
    }


# =====================================================
# DOWNLOAD CLEANED DATASET
# =====================================================

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
        filename=f"{dataset_id}_cleaned.csv"
    )
