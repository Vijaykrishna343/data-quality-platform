from fastapi import APIRouter, HTTPException
import pandas as pd
import os

from backend.core.file_manager import read_csv

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "storage", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


from backend.engines.scoring_engine import ScoringEngine
def calculate_importance(df):
    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return {}

    importance = numeric_df.var().sort_values(ascending=False)

    return {
        col: round(val, 2)
        for col, val in importance.items()
    }


@router.get("/{dataset_id}")
def get_profile(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = read_csv(file_path)

    rows = len(df)
    cols = len(df.columns)

    total_cells = rows * cols

    quality_score, missing_pct, duplicate_pct, _, _ = ScoringEngine.calculate_metrics_and_score(df, "iqr")
    importance = calculate_importance(df)

    return {
        "rows": rows,
        "columns": cols,
        "missing_percentage": round(missing_pct, 2),
        "duplicate_percentage": round(duplicate_pct, 2),
        "quality_score": quality_score,
        "importance": importance
    }