from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import pandas as pd

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    dataset_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    pd.read_csv(file_path)

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "message": "File uploaded successfully"
    }