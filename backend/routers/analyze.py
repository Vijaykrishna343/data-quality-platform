from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.services.profiler import profile_data
from backend.services.scorer import calculate_quality_score

router = APIRouter(prefix="/analyze", tags=["Analyze"])

@router.post("/")
async def analyze_dataset(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    profile = profile_data(df)
    score, reasons = calculate_quality_score(profile)

    return {
        "rows": profile["rows"],
        "columns": profile["columns"],
        "quality_score": score,
        "reasons": reasons
    }