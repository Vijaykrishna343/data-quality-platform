from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.services.profiler import profile_data
from backend.services.scorer import calculate_quality_score
from backend.services.importance import calculate_column_importance

router = APIRouter(prefix="/analyze", tags=["Analyze"])


@router.post("/")
async def analyze_dataset(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
    except Exception:
        return {"error": "Invalid or corrupted CSV file."}

    profile = profile_data(df)
    quality_score, reasons = calculate_quality_score(profile)
    column_importance = calculate_column_importance(df)

    return {
        "rows": profile["rows"],
        "columns": profile["columns"],
        "missing_values": profile["missing_values"],
        "duplicate_rows": profile["duplicate_rows"],
        "outlier_count": profile["outlier_count"],
        "quality_score": quality_score,
        "reasons": reasons,
        "column_importance": column_importance
    }