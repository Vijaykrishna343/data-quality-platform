from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Dataset
from backend.config import UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
from backend.core.file_manager import read_csv
from backend.schemas.response_models import UploadResponse
import os
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and validate a CSV file"""
    file_path = None
    try:
        filename = file.filename or "dataset.csv"
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Only CSV files allowed")

        # ✅ Use UUID for file storage (NOT DB ID)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")

        # Save file
        file_size_bytes = 0
        max_file_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                file_size_bytes += len(chunk)
                if file_size_bytes > max_file_size_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit"
                    )
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
            name=filename,
            file_path=file_path
        )

        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)
        
        logger.info(f"Dataset uploaded successfully: {new_dataset.id}")

    except HTTPException:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV file: {str(e)}"
        )
    finally:
        await file.close()

    return UploadResponse(
        dataset_id=new_dataset.id,
        filename=filename,
        message="File uploaded successfully"
    )
