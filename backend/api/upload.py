from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import pandas as pd

router = APIRouter()

BASE_STORAGE = "backend/storage"
UPLOAD_DIR = os.path.join(BASE_STORAGE, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    dataset_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    try:
        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        # 🔥 Try multiple parsing strategies
        try:
            df = pd.read_csv(file_path)
        except:
            try:
                df = pd.read_csv(file_path, encoding="latin1")
            except:
                try:
                    df = pd.read_csv(file_path, sep=";")
                except:
                    df = pd.read_csv(file_path, sep=None, engine="python")

        # 🚨 Check if dataframe empty
        if df.empty:
            raise Exception("Empty CSV file")

        # 🚨 Check if only 1 column (bad parsing)
        if len(df.columns) <= 1:
            raise Exception("Invalid CSV format or wrong delimiter")

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid or unsupported CSV format: {str(e)}"
        )

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "message": "File uploaded successfully"
    }