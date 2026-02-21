from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.services.cleaner import clean_data
from backend.services.profiler import profile_data
from backend.services.scorer import calculate_quality_score

router = APIRouter(prefix="/clean", tags=["Clean"])

@router.post("/")
async def clean_dataset(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    cleaned = clean_data(df)

    profile = profile_data(cleaned)
    score, reasons = calculate_quality_score(profile)

    return {
        "rows_after_cleaning": cleaned.shape[0],
        "quality_score": score,
        "reasons": reasons
    }