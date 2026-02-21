from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.services.profiler import profile_data
from backend.services.recommendation_engine import generate_recommendations

router = APIRouter(prefix="/recommend", tags=["Recommend"])

@router.post("/")
async def recommend_dataset(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    profile = profile_data(df)
    recommendations = generate_recommendations(profile)

    return {
        "recommendations": recommendations
    }