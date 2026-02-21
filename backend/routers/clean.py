from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.services.profiler import profile_data
from backend.services.scorer import calculate_quality_score
from backend.services.cleaner import clean_data

router = APIRouter(prefix="/clean", tags=["Clean"])


@router.post("/")
async def clean_dataset(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
    except Exception:
        return {"error": "Invalid or corrupted CSV file."}

    # ---- Before Cleaning ----
    profile_before = profile_data(df)
    score_before, _ = calculate_quality_score(profile_before)

    # ---- Perform Cleaning ----
    cleaned_df = clean_data(df)

    # ---- After Cleaning ----
    profile_after = profile_data(cleaned_df)
    score_after, _ = calculate_quality_score(profile_after)

    improvement = round(score_after - score_before, 2)

    return {
        "rows_before": profile_before["rows"],
        "rows_after": profile_after["rows"],
        "quality_score_before": score_before,
        "quality_score_after": score_after,
        "improvement": improvement
    }