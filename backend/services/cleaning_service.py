import os
import pandas as pd

from engines.cleaning_engine import clean_dataframe
from engines.outlier_engine import calculate_outlier_percentage
from engines.scoring_engine import ScoringEngine


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "storage", "uploads")
CLEANED_DIR = os.path.join(BASE_DIR, "storage", "cleaned")

os.makedirs(CLEANED_DIR, exist_ok=True)


def calculate_missing_percentage(df):
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 0
    return (df.isnull().sum().sum() / total_cells) * 100


def calculate_duplicate_percentage(df):
    if len(df) == 0:
        return 0
    return (df.duplicated().sum() / len(df)) * 100


def clean_file(dataset_id: str, options: dict):
    """
    Performs cleaning + returns before/after analytics
    """

    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError("Dataset not found")

    # ================= BEFORE CLEANING =================
    df_before = pd.read_csv(file_path)

    missing_before = calculate_missing_percentage(df_before)
    duplicate_before = calculate_duplicate_percentage(df_before)
    outlier_before = calculate_outlier_percentage(df_before)

    score_before = ScoringEngine.calculate_score(
        missing_before,
        duplicate_before,
        outlier_before,
    )

    # ================= CLEANING =================
    df_after = clean_dataframe(df_before, options)

    # ================= AFTER CLEANING =================
    missing_after = calculate_missing_percentage(df_after)
    duplicate_after = calculate_duplicate_percentage(df_after)
    outlier_after = calculate_outlier_percentage(df_after)

    score_after = ScoringEngine.calculate_score(
        missing_after,
        duplicate_after,
        outlier_after,
    )

    ml_readiness = ScoringEngine.get_ml_readiness(score_after)

    # ================= SAVE CLEANED FILE =================
    cleaned_path = os.path.join(CLEANED_DIR, f"{dataset_id}.csv")
    df_after.to_csv(cleaned_path, index=False)

    return {
        "before": {
            "missing_pct": round(missing_before, 2),
            "duplicate_pct": round(duplicate_before, 2),
            "outlier_pct": round(outlier_before, 2),
            "score": score_before,
        },
        "after": {
            "missing_pct": round(missing_after, 2),
            "duplicate_pct": round(duplicate_after, 2),
            "outlier_pct": round(outlier_after, 2),
            "score": score_after,
        },
        "ml_readiness": ml_readiness,
        "cleaned_rows": len(df_after),
        "original_rows": len(df_before),
    }