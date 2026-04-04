import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.file_manager import read_csv
from backend.database import get_db
from backend.engines.scoring_engine import ScoringEngine
from backend.models import Dataset
from backend.schemas.response_models import ProfileResponse

router = APIRouter()


def calculate_importance(df):
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return {}

    importance = numeric_df.var().sort_values(ascending=False)
    return {col: round(float(val), 2) for col, val in importance.items()}


@router.get("/{dataset_id}", response_model=ProfileResponse)
def get_profile(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    df = read_csv(file_path)
    rows = len(df)
    cols = len(df.columns)
    quality_score, missing_pct, duplicate_pct, _, _ = (
        ScoringEngine.calculate_metrics_and_score(df, "iqr")
    )

    return ProfileResponse(
        rows=rows,
        columns=cols,
        missing_percentage=round(missing_pct, 2),
        duplicate_percentage=round(duplicate_pct, 2),
        quality_score=quality_score,
        importance=calculate_importance(df),
    )
