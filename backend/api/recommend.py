import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.file_manager import read_csv
from backend.database import get_db
from backend.models import Dataset
from backend.schemas.response_models import RecommendationResponse

router = APIRouter()

@router.get("/{dataset_id}", response_model=RecommendationResponse)
def recommend(dataset_id: int, db: Session = Depends(get_db)):
    # Get dataset from database
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = dataset.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    df = read_csv(file_path)

    recommendations = []

    if df.isnull().sum().sum() > 0:
        recommendations.append("Dataset contains missing values.")

    if df.duplicated().sum() > 0:
        recommendations.append("Dataset contains duplicate rows.")

    return RecommendationResponse(recommendations=recommendations)
