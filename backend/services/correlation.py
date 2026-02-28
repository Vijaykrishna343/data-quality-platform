import pandas as pd
import numpy as np


# =====================================================
# CORRELATION MATRIX
# =====================================================

def calculate_correlation_matrix(df: pd.DataFrame):

    numeric_df = df.select_dtypes(include=["number"])

    # Need at least 2 numeric columns
    if numeric_df.shape[1] < 2:
        return {}

    corr_matrix = numeric_df.corr()

    # Replace NaN / inf safely
    corr_matrix = corr_matrix.replace([np.inf, -np.inf], 0)
    corr_matrix = corr_matrix.fillna(0).round(3)

    return corr_matrix.to_dict()


# =====================================================
# HEATMAP DATA (UI Friendly Format)
# =====================================================

def generate_heatmap_data(df: pd.DataFrame, max_features: int = 25):

    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.shape[1] < 2:
        return []

    # Limit features to prevent huge payload
    numeric_df = numeric_df.iloc[:, :max_features]

    corr_matrix = numeric_df.corr()

    corr_matrix = corr_matrix.replace([np.inf, -np.inf], 0)
    corr_matrix = corr_matrix.fillna(0)

    heatmap_data = []

    for row in corr_matrix.index:
        for col in corr_matrix.columns:
            heatmap_data.append({
                "x": row,
                "y": col,
                "value": round(float(corr_matrix.loc[row, col]), 3)
            })

    return heatmap_data


# =====================================================
# STRONG CORRELATION DETECTION
# =====================================================

def detect_strong_correlations(
    df: pd.DataFrame,
    threshold: float = 0.8,
    max_pairs: int = 20
):

    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.shape[1] < 2:
        return []

    corr_matrix = numeric_df.corr()

    corr_matrix = corr_matrix.replace([np.inf, -np.inf], 0)
    corr_matrix = corr_matrix.fillna(0)

    strong_pairs = []

    columns = corr_matrix.columns

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):

            value = corr_matrix.iloc[i, j]

            if abs(value) >= threshold:
                strong_pairs.append({
                    "feature_1": columns[i],
                    "feature_2": columns[j],
                    "correlation": round(float(value), 3)
                })

    # Sort strongest first
    strong_pairs = sorted(
        strong_pairs,
        key=lambda x: abs(x["correlation"]),
        reverse=True
    )

    # Limit payload
    return strong_pairs[:max_pairs]