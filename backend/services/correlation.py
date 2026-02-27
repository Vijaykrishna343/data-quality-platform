import pandas as pd
import os


def calculate_correlation_matrix(df: pd.DataFrame):
    """
    Returns full correlation matrix (numeric only)
    """

    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return {}

    corr_matrix = numeric_df.corr().fillna(0).round(3)

    return corr_matrix.to_dict()


def generate_heatmap_data(df: pd.DataFrame):
    """
    Returns visualization-ready heatmap structure
    """

    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return []

    corr_matrix = numeric_df.corr().fillna(0)

    heatmap_data = []

    for row in corr_matrix.index:
        for col in corr_matrix.columns:
            heatmap_data.append({
                "x": row,
                "y": col,
                "value": round(float(corr_matrix.loc[row, col]), 3)
            })

    return heatmap_data


def detect_strong_correlations(df: pd.DataFrame, threshold: float = 0.8):
    """
    Detects strong feature relationships
    """

    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return []

    corr_matrix = numeric_df.corr().fillna(0)

    strong_pairs = []

    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):

            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            value = corr_matrix.iloc[i, j]

            if abs(value) >= threshold:
                strong_pairs.append({
                    "feature_1": col1,
                    "feature_2": col2,
                    "correlation": round(float(value), 3)
                })

    # Sort strongest first
    strong_pairs = sorted(
        strong_pairs,
        key=lambda x: abs(x["correlation"]),
        reverse=True
    )

    return strong_pairs