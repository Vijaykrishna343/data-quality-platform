from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

UPLOAD_DIR = "backend/storage/uploads"


@router.get("/{dataset_id}")
def recommend(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    recommendations = []

    if df.isnull().sum().sum() > 0:
        recommendations.append("Dataset contains missing values.")

    if df.duplicated().sum() > 0:
        recommendations.append("Dataset contains duplicate rows.")

    return {"recommendations": recommendations}