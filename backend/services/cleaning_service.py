import os

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.config import CLEANED_DIR
from backend.core.file_manager import read_csv
from backend.database import SessionLocal
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine
from backend.models import Dataset


os.makedirs(CLEANED_DIR, exist_ok=True)


def calculate_missing_percentage(df: pd.DataFrame) -> float:
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0.0
    return float((df.isnull().sum().sum() / total_cells) * 100)


def calculate_duplicate_percentage(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return float((df.duplicated().sum() / len(df)) * 100)


def calculate_outlier_percentage(df: pd.DataFrame, method: str = "iqr") -> float:
    return float(OutlierEngine.detect_percentage(df, method))


def clean_dataframe(df: pd.DataFrame, options: dict) -> pd.DataFrame:
    df_clean = df.copy()

    # 1. Normalize All Strategy Strings (HIGH PRIORITY)
    missing_method = options.get("missing_method", "none").strip().lower()
    duplicate_method = options.get("duplicate_method", "none").strip().lower()
    outlier_method = options.get("outlier_method", "none").strip().lower()
    noisy_method = options.get("noisy_method", "none").strip().lower()
    outlier_action = options.get("outlier_action", "fix").strip().lower()
    noisy_action = options.get("noisy_action", "fix").strip().lower()

    drop_columns = options.get("drop_columns", [])
    if drop_columns:
        df_clean = df_clean.drop(columns=drop_columns, errors="ignore")

    # ---- Missing value handling ----
    if missing_method != "none":
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        from backend.engines.imputation_engine import ImputationEngine
        
        if missing_method in ("smart", "knn"):
            df_clean = ImputationEngine.impute_missing(df_clean, n_neighbors=5)
        elif missing_method == "mean" and not numeric_cols.empty:
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        elif missing_method == "median" and not numeric_cols.empty:
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        elif missing_method == "mode":
            for col in df_clean.columns:
                mode_val = df_clean[col].mode()
                if not mode_val.empty:
                    df_clean[col] = df_clean[col].fillna(mode_val.iloc[0])

    # ---- Fix Missing Duplicate Cleaning Logic (HIGH PRIORITY) ----
    if duplicate_method != "none":
        if len(df_clean) > 50000:
            # Fast exact removal for large datasets
            df_clean = df_clean.drop_duplicates()
        else:
            # Standard removal first
            df_clean = df_clean.drop_duplicates()
            # Then attempt fuzzy removal if engine is functional
            try:
                from backend.engines.duplicate_engine import DuplicateEngine
                df_clean = DuplicateEngine.remove_fuzzy_duplicates(
                    df_clean, list(df_clean.columns), threshold=90.0
                )
            except Exception:
                # Fallback to just exact duplicates if fuzzy engine fails
                pass

    # ---- Outlier handling ----
    if outlier_method != "none":
        if outlier_action == "remove":
            df_clean = OutlierEngine.remove_outliers(df_clean, outlier_method)
        else:
            df_clean = OutlierEngine.fix_outliers(df_clean, outlier_method)

    # ---- Noisy data handling (treated as accuracy issue) ----
    if noisy_method != "none":
        if noisy_action == "remove":
            df_clean = OutlierEngine.remove_outliers(df_clean, noisy_method)
        else:
            df_clean = OutlierEngine.fix_noise(df_clean, noisy_method)

    return df_clean.replace([np.inf, -np.inf], np.nan)


def _get_dataset(dataset_id: int, db: Session) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise FileNotFoundError("Dataset not found")
    if not os.path.exists(dataset.file_path):
        raise FileNotFoundError("Dataset file not found")
    return dataset


def clean_file(dataset_id: int, options: dict, db: Session | None = None):
    """
    Perform cleaning for a stored dataset and return before/after analytics.
    """
    owns_session = db is None
    if owns_session:
        db = SessionLocal()

    try:
        dataset = _get_dataset(dataset_id, db)
        df_before = read_csv(dataset.file_path)
        df_after = clean_dataframe(df_before, options)

        before_score, missing_before, duplicate_before, outlier_before, noisy_before = (
            ScoringEngine.calculate_metrics_and_score(df_before, "iqr")
        )
        
        # Determine method for post-cleaning scoring
        calc_outlier_method = options.get("outlier_method", "iqr").strip().lower()
        if calc_outlier_method == "none" or not calc_outlier_method:
            calc_outlier_method = "iqr"
        if calc_outlier_method == "isolation":
            calc_outlier_method = "isolation_forest"

        after_score, missing_after, duplicate_after, outlier_after, noisy_after = (
            ScoringEngine.calculate_metrics_and_score(df_after, calc_outlier_method)
        )

        cleaned_path = os.path.join(CLEANED_DIR, f"{dataset.id}.csv")
        df_after.to_csv(cleaned_path, index=False)

        # Calculate improvement delta
        improvement = round(after_score - before_score, 2)

        return {
            "before": {
                "missing_pct": round(missing_before, 2),
                "duplicate_pct": round(duplicate_before, 2),
                "outlier_pct": round(outlier_before, 2),
                "noisy_pct": round(noisy_before, 2),
                "score": round(before_score, 2),
            },
            "after": {
                "missing_pct": round(missing_after, 2),
                "duplicate_pct": round(duplicate_after, 2),
                "outlier_pct": round(outlier_after, 2),
                "noisy_pct": round(noisy_after, 2),
                "score": round(after_score, 2),
            },
            "improvement": improvement,
            "ml_readiness": ScoringEngine.get_ml_readiness(after_score),
            "cleaned_rows": len(df_after),
            "original_rows": len(df_before),
            "rows_removed": len(df_before) - len(df_after),
            "cleaned_path": cleaned_path,
        }

    finally:
        if owns_session and db is not None:
            db.close()
