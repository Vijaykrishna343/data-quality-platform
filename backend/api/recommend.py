from fastapi import APIRouter, HTTPException
import pandas as pd
import os

from backend.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

UPLOAD_DIR = "backend/uploads"


@router.get("/{dataset_id}")
def get_recommendations(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    recommendations = RecommendationService.generate(df)

    return {"recommendations": recommendations}