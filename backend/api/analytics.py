from fastapi import APIRouter, HTTPException, Depends
import os
import pandas as pd
import numpy as np
import json

from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import AnalysisResult, Dataset

from backend.engines.scoring_engine import ScoringEngine
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.importance_engine import ImportanceEngine
from backend.engines.completeness_engine import CompletenessEngine
from backend.services.correlation import (
    calculate_correlation_matrix,
    detect_strong_correlations
)
from backend.services.recommendation_service import RecommendationService
from backend.core.file_manager import read_csv

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ✅ Clean NaN safely
def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj


@router.get("/{dataset_id}")
def get_full_analytics(dataset_id: int, db: Session = Depends(get_db)):

    # ✅ GET DATASET FROM DB
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = dataset.file_path
    meta_path = file_path.replace(".csv", "_meta.json")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    auto_clean_report = {}

    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            auto_clean_report = json.load(f)
        df = read_csv(file_path)
    else:
        df = read_csv(file_path)

        initial_rows = len(df)
        df = df.drop_duplicates(keep="first")
        duplicates_removed = initial_rows - len(df)

        auto_clean_report = {
            "duplicates_removed": duplicates_removed
        }

        df.to_csv(file_path, index=False)

        with open(meta_path, "w") as f:
            json.dump(auto_clean_report, f)

    total_rows = len(df)
    total_cols = len(df.columns)

    df_sampled = df.sample(n=10000, random_state=42) if total_rows > 10000 else df

    quality_score, missing_percentage, duplicate_percentage, outlier_pct, noisy_percentage = ScoringEngine.calculate_metrics_and_score(df, "iqr")

    missing_count = int(df.isnull().any(axis=1).sum())
    duplicate_count = int(df.duplicated(keep="first").sum())

    completeness = CompletenessEngine.calculate(df)

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    boolean_columns = df.select_dtypes(include=["bool"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime"]).columns.tolist()

    raw_categorical = df.select_dtypes(include=["object"]).columns.tolist()
    categorical_columns = []
    alphanumeric_columns = []

    for col in raw_categorical:
        series_str = df[col].astype(str)
        if (series_str.str.contains(r'[a-zA-Z]') & series_str.str.contains(r'[0-9]')).any():
            alphanumeric_columns.append(col)
        else:
            categorical_columns.append(col)

    importance = ImportanceEngine.calculate(df_sampled)
    column_outliers = OutlierEngine.detect_column_outliers(df_sampled, "iqr")

    correlation_matrix = calculate_correlation_matrix(df_sampled)
    strong_pairs = detect_strong_correlations(df_sampled)

    correlation_matrix = {
        k: {kk: float(vv) for kk, vv in v.items()}
        for k, v in correlation_matrix.items()
    }

    recommendations = RecommendationService.generate(df_sampled)
    readiness_data = ScoringEngine.get_ml_readiness(quality_score)

    response = {
        "profile": {
            "rows": total_rows,
            "columns": total_cols,
            "missing_count": missing_count,
            "duplicate_count": duplicate_count,
            "quality_score": round(quality_score, 2),
            "completeness": round(completeness, 2),
        },
        "ml_readiness": {
            "label": readiness_data["status"],
            "color": readiness_data["color"]
        },
        "data_types": {
            "numeric": numeric_columns,
            "categorical": categorical_columns,
            "alphanumeric": alphanumeric_columns,
            "boolean": boolean_columns,
            "datetime": datetime_columns,
        },
        "importance": importance,
        "outliers": {
            "overall_percentage": round(outlier_pct, 2),
            "noisy_percentage": round(noisy_percentage, 2),
            "column_outliers": column_outliers,
            "breakdown": ScoringEngine.score_breakdown(
                missing_percentage,
                duplicate_percentage,
                outlier_pct,
                noisy_percentage
            )
        },
        "correlation": {
            "matrix": correlation_matrix,
            "strong_pairs": strong_pairs,
        },
        "auto_clean_report": auto_clean_report,
        "ai_review": recommendations
    }

    # ✅ CLEAN JSON
    cleaned_response = clean_nan(response)

    # ✅ SAVE TO DB
    new_result = AnalysisResult(
        dataset_id=dataset_id,
        result=cleaned_response
    )

    db.add(new_result)
    db.commit()

    return cleaned_response