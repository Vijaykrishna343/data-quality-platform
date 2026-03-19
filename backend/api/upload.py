from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import pandas as pd

from backend.core.file_manager import read_csv

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    dataset_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    try:
        # Use chunked streaming instead of loading entire file into memory
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                f.write(chunk)

        # 🔥 Fast CSV validation (only read first 5 rows) using robust read_csv
        try:
            df = read_csv(file_path, sep=None, engine="python", nrows=5)
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

        if df.empty:
            raise ValueError("CSV file is empty")

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV file: {str(e)}"
        )

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "message": "File uploaded successfully"
    }