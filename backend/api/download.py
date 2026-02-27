from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import pandas as pd
import math

router = APIRouter(prefix="/download", tags=["Download"])

UPLOAD_DIR = "backend/uploads"
CLEANED_DIR = "backend/storage/cleaned"

# ================= PREVIEW (PAGINATION) =================

@router.get("/preview/{dataset_id}")
def preview_dataset(dataset_id: str, page: int = 1, page_size: int = 20):

    file_path = os.path.join(CLEANED_DIR, f"{dataset_id}.csv")

    # If cleaned version not available, use original
    if not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    total_rows = len(df)
    total_pages = math.ceil(total_rows / page_size)

    start = (page - 1) * page_size
    end = start + page_size

    page_df = df.iloc[start:end]

    return {
        "columns": list(df.columns),
        "rows": page_df.fillna("").to_dict(orient="records"),
        "total_pages": total_pages,
        "current_page": page
    }


# ================= DOWNLOAD CLEANED FILE =================

@router.get("/{dataset_id}")
def download_dataset(dataset_id: str):

    file_path = os.path.join(CLEANED_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    return FileResponse(
        path=file_path,
        filename="cleaned_dataset.csv",
        media_type="text/csv"
    )