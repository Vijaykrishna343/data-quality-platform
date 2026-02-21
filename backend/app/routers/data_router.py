from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.app.services.analysis import analyze_data
from backend.app.services.importance import column_importance
from backend.app.services.recommendations import generate_recommendations

router = APIRouter()


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    return analyze_data(df)


@router.post("/importance")
async def importance(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    return column_importance(df)


@router.post("/recommendations")
async def recommendations(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    return {"recommendations": generate_recommendations(df)}