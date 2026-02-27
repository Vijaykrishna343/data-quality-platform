from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"


@router.get("/{dataset_id}")
def classify(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object"]).columns.tolist()

    return {
        "numeric": numeric,
        "categorical": categorical
    }