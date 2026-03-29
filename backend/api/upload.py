from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Dataset
import os
import uuid

from backend.core.file_manager import read_csv

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    # ✅ Use UUID for file storage (NOT DB ID)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")

    try:
        # Save file
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

        # Validate CSV
        try:
            df = read_csv(file_path, sep=None, engine="python", nrows=5)
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

        if df.empty:
            raise ValueError("CSV file is empty")

        # ✅ Save dataset in DB
        new_dataset = Dataset(
            name=file.filename,
            file_path=file_path
        )

        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV file: {str(e)}"
        )

    return {
        "dataset_id": new_dataset.id,  # DB ID (important)
        "filename": file.filename,
        "message": "File uploaded successfully"
    }