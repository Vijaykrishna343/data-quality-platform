import pandas as pd
import numpy as np


def calculate_column_importance(df: pd.DataFrame):
    """
    Calculates importance score (0–100) for each column based on:
    - Missing ratio
    - Variance (numeric)
    - Unique ratio (categorical)
    """

    importance_scores = {}

    for column in df.columns:
        col_data = df[column]

        # ---- Missing Score ----
        missing_ratio = col_data.isnull().mean()
        missing_score = (1 - missing_ratio) * 100

        # ---- Information Score ----
        if pd.api.types.is_numeric_dtype(col_data):
            variance = col_data.var()
            information_score = min(variance / (variance + 1), 1) * 100 if variance else 0
        else:
            unique_ratio = col_data.nunique() / len(col_data) if len(col_data) > 0 else 0
            information_score = unique_ratio * 100

        # ---- Final Importance ----
        final_score = 0.5 * missing_score + 0.5 * information_score
        final_score = round(max(0, min(final_score, 100)), 2)

        importance_scores[column] = final_score

    return importance_scores