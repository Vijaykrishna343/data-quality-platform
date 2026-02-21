import pandas as pd

def profile_data(df: pd.DataFrame):
    missing_total = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_total": missing_total,
        "duplicates": duplicates
    }