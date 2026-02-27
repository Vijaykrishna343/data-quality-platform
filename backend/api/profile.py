from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "storage", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


def calculate_quality_score(df):
    total_cells = df.shape[0] * df.shape[1]

    if total_cells == 0:
        return 0

    missing_ratio = df.isnull().sum().sum() / total_cells
    duplicate_ratio = df.duplicated().sum() / len(df)

    score = 100 - ((missing_ratio * 50) + (duplicate_ratio * 50))
    return round(max(score, 0), 2)


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

    df = pd.read_csv(file_path)

    rows = len(df)
    cols = len(df.columns)

    total_cells = rows * cols

    missing_pct = (
        (df.isnull().sum().sum() / total_cells) * 100
        if total_cells > 0 else 0
    )

    duplicate_pct = (
        (df.duplicated().sum() / rows) * 100
        if rows > 0 else 0
    )

    quality_score = calculate_quality_score(df)
    importance = calculate_importance(df)

    return {
        "rows": rows,
        "columns": cols,
        "missing_percentage": round(missing_pct, 2),
        "duplicate_percentage": round(duplicate_pct, 2),
        "quality_score": quality_score,
        "importance": importance
    }