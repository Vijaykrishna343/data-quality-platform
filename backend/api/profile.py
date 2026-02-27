from fastapi import APIRouter, HTTPException
import pandas as pd
import os

from backend.engines.importance_engine import ImportanceEngine

router = APIRouter(prefix="/profile", tags=["Profile"])

UPLOAD_DIR = "backend/uploads"


@router.get("/{dataset_id}")
def get_profile(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    missing_pct = (
        (df.isnull().sum().sum() / total_cells) * 100
        if total_cells > 0 else 0
    )

    duplicate_pct = (
        (df.duplicated().sum() / total_rows) * 100
        if total_rows > 0 else 0
    )

    importance = ImportanceEngine.calculate(df)

    return {
        "rows": total_rows,
        "columns": total_cols,
        "missing_percentage": round(missing_pct, 2),
        "duplicate_percentage": round(duplicate_pct, 2),
        "importance": importance
    }