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

import json

from backend.core.file_manager import read_csv

router = APIRouter(prefix="/analytics", tags=["Analytics"])

UPLOAD_DIR = "backend/storage/uploads"


# ✅ Helper function to clean NaN safely from any object
def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj


# ✅ NEW: Precise Cell-wise Outlier Percentage (IQR) fully vectorized
def calculate_outlier_percentage(df):
    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return 0.0

    Q1 = numeric_df.quantile(0.25)
    Q3 = numeric_df.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outlier_mask = (numeric_df < lower_bound) | (numeric_df > upper_bound)
    outlier_cells = outlier_mask.sum().sum()
    total_cells = numeric_df.size

    return round((outlier_cells / total_cells) * 100, 2)


@router.get("/{dataset_id}")
def get_full_analytics(dataset_id: str):

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")
    meta_path = os.path.join(UPLOAD_DIR, f"{dataset_id}_meta.json")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    auto_clean_report = {}

    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            auto_clean_report = json.load(f)
        df = read_csv(file_path)
    else:
        df = read_csv(file_path)

        # 1. Deduplication
        initial_rows = len(df)
        df = df.drop_duplicates(keep="first")
        duplicates_removed = initial_rows - len(df)

        # 2. Priority-Based Hierarchical Sorting
        priority_keywords = ["year", "month", "date", "day", "time", "timestamp"]
        sort_columns = []
        
        # First: Search for columns that match priority keywords exactly or as partial strings
        for keyword in priority_keywords:
            for col in df.columns:
                col_lower = col.lower()
                if keyword in col_lower and col not in sort_columns:
                    # Avoid picking id columns that happen to contain 'day' etc (e.g. 'dataset_id')
                    if "id" not in col_lower or keyword in col_lower:
                         sort_columns.append(col)

        # Second: If no priority columns found, use existing Robust DateTime Detection for a fallback
        if not sort_columns:
            found_date_col = None
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    found_date_col = col
                    break
                
                is_potential_date_name = any(kw in col.lower() for kw in ["date", "time", "timestamp"])
                if is_potential_date_name or df[col].dtype == 'object':
                    try:
                        sample_series = df[col].dropna().head(30)
                        if not sample_series.empty:
                            parsed_sample = pd.to_datetime(sample_series, errors='coerce')
                            valid_ratio = parsed_sample.notnull().mean()
                            if valid_ratio >= 0.7:
                                avg_len = sample_series.astype(str).str.len().mean()
                                if avg_len > 8 or is_potential_date_name:
                                    df[col] = pd.to_datetime(df[col], errors='coerce')
                                    found_date_col = col
                                    break
                    except:
                        continue
            if found_date_col:
                sort_columns = [found_date_col]

        if sort_columns:
            df = df.sort_values(by=sort_columns, ascending=True)
            sort_message = f"Dataset sorted by priority columns: {', '.join(sort_columns)}"
        else:
            sort_message = "No priority or datetime columns detected for sorting."

        auto_clean_report = {
            "sort_message": sort_message,
            "duplicates_removed": duplicates_removed
        }

        # Save cleaned df permanently
        df.to_csv(file_path, index=False)

        # Save metadata
        with open(meta_path, "w") as f:
            json.dump(auto_clean_report, f)

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # ================= SAMPLING FOR HEAVY ENGINES =================
    if total_rows > 10000:
        df_sampled = df.sample(n=10000, random_state=42)
    else:
        df_sampled = df

    # ================= METRICS & SCORING =================
    # Use full DF for basic metrics to ensure consistency with simulate.py
    quality_score, missing_percentage, duplicate_percentage, outlier_pct, noisy_percentage = ScoringEngine.calculate_metrics_and_score(df, "iqr")

    # The frontend expects counts, not percentages for the profile display
    missing_count = int(df.isnull().any(axis=1).sum()) # ANY cell missing makes the row "missing"
    duplicate_count = int(df.duplicated(keep="first").sum())


    completeness = CompletenessEngine.calculate(df)

    # Advanced Data Type Classification
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    
    # Identify boolean and datetime first
    boolean_columns = df.select_dtypes(include=["bool"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime"]).columns.tolist()

    # Identify categorical and alphanumeric
    raw_categorical = df.select_dtypes(include=["object"]).columns.tolist()
    categorical_columns = []
    alphanumeric_columns = []

    for col in raw_categorical:
        # Check if the column contains strings with both letters and numbers
        series_str = df[col].astype(str)
        has_letters = series_str.str.contains(r'[a-zA-Z]', regex=True)
        has_numbers = series_str.str.contains(r'[0-9]', regex=True)
        
        if (has_letters & has_numbers).any():
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

    # ================= ML READINESS =================
    readiness_data = ScoringEngine.get_ml_readiness(quality_score)
    readiness = readiness_data["status"]
    badge_color = readiness_data["color"]

    # ================= SAFE JSON CLEANING =================
    df_clean = df.replace([np.inf, -np.inf], np.nan)
    preview_rows = df_clean.head(20).where(
        pd.notnull(df_clean), None
    ).to_dict(orient="records")

    # ================= RETURN RESPONSE =================
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
            "label": readiness,
            "color": badge_color
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
            "breakdown": ScoringEngine.score_breakdown(missing_percentage, duplicate_percentage, outlier_pct, noisy_percentage)
        },
        "correlation": {
            "matrix": correlation_matrix,
            "strong_pairs": strong_pairs,
        },
        "auto_clean_report": auto_clean_report,
        "ai_review": recommendations
    }

    return clean_nan(response)