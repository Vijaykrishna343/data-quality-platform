import pandas as pd

def profile_dataset(df: pd.DataFrame):

    profile = {}

    for col in df.columns:
        profile[col] = {
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "missing_percent": round(
                (df[col].isna().sum() / len(df)) * 100, 2
            ),
            "unique_values": int(df[col].nunique())
        }

    return profile