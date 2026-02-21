import pandas as pd

def analyze_data(df: pd.DataFrame):

    rows = len(df)
    columns = len(df.columns)

    missing_ratio = df.isnull().mean().mean()
    score = round((1 - missing_ratio) * 100, 2)

    reasons = []

    if missing_ratio > 0.2:
        reasons.append("High missing values detected.")

    if df.duplicated().sum() > 0:
        reasons.append("Duplicate rows detected.")

    column_types = {
        "Numerical": df.select_dtypes(include=["int64", "float64"]).columns.tolist(),
        "Categorical": df.select_dtypes(include=["object"]).columns.tolist(),
    }

    return {
        "rows": rows,
        "columns": columns,
        "quality_score": score,
        "reasons": reasons,
        "column_types": column_types
    }