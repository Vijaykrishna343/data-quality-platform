from fastapi import APIRouter, HTTPException
import os
import pandas as pd
import numpy as np

from backend.engines.scoring_engine import ScoringEngine
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.importance_engine import ImportanceEngine
from backend.engines.completeness_engine import CompletenessEngine
from backend.services.correlation import (
    calculate_correlation_matrix,
    detect_strong_correlations
)
from backend.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

UPLOAD_DIR = "backend/storage/uploads"


@router.get("/{dataset_id}")
def get_full_analytics(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(file_path)

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    missing_pct = (df.isnull().sum().sum() / total_cells) * 100 if total_cells else 0
    duplicate_pct = (df.duplicated().sum() / total_rows) * 100 if total_rows else 0
    outlier_pct = OutlierEngine.detect_percentage(df, "iqr")

    quality_score = ScoringEngine.calculate_score(
        missing_pct,
        duplicate_pct,
        outlier_pct
    )

    completeness = CompletenessEngine.calculate(df)

    # Advanced Data Type Classification
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()
    boolean_columns = df.select_dtypes(include=["bool"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime"]).columns.tolist()

    importance = ImportanceEngine.calculate(df)

    column_outliers = OutlierEngine.detect_column_outliers(df, "iqr")

    correlation_matrix = calculate_correlation_matrix(df)
    strong_pairs = detect_strong_correlations(df)

    correlation_matrix = {
        k: {kk: float(vv) for kk, vv in v.items()}
        for k, v in correlation_matrix.items()
    }

    recommendations = RecommendationService.generate(df)

    # 🔥 ML READINESS REMOVED FROM ANALYTICS

    return {
        "profile": {
            "rows": total_rows,
            "columns": total_cols,
            "missing_percentage": round(missing_pct, 2),
            "duplicate_percentage": round(duplicate_pct, 2),
            "quality_score": round(quality_score, 2),
            "completeness": round(completeness, 2),
        },
        "data_types": {
            "numeric": numeric_columns,
            "categorical": categorical_columns,
            "boolean": boolean_columns,
            "datetime": datetime_columns,
        },
        "importance": importance,
        "outliers": {
            "overall_percentage": outlier_pct,
            "column_outliers": column_outliers,
        },
        "correlation": {
            "matrix": correlation_matrix,
            "strong_pairs": strong_pairs,
        },
        "ai_review": recommendations
    }