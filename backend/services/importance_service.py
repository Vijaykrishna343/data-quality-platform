import pandas as pd


def calculate_importance(file_path: str):

    df = pd.read_csv(file_path)
    numeric_df = df.select_dtypes(include=["number"])

    importance_scores = []

    if numeric_df.empty:
        return []

    corr_matrix = numeric_df.corr()
    max_variance = numeric_df.var().max()

    for col in numeric_df.columns:

        variance = numeric_df[col].var()
        V = (variance / max_variance) * 100 if max_variance else 0

        R = abs(corr_matrix[col]).mean() * 100
        Q = (1 - df[col].isna().mean()) * 100

        score = 0.4 * V + 0.3 * R + 0.3 * Q

        importance_scores.append({
            "column": col,
            "score": round(score, 2)
        })

    return importance_scores