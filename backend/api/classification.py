from fastapi import APIRouter, HTTPException
import pandas as pd
import os

from backend.engines.classification_engine import ClassificationEngine

router = APIRouter(prefix="/classify", tags=["Classification"])

UPLOAD_DIR = "backend/uploads"


@router.get("/{dataset_id}")
def classify_columns(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    result = ClassificationEngine.classify(df)

    return result