import pandas as pd

def compute_quality_metrics(df: pd.DataFrame) -> dict:

    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()

    completeness = ((total_cells - missing_cells) / total_cells) * 100 if total_cells else 0

    duplicate_rows = df.duplicated().sum()
    uniqueness = ((len(df) - duplicate_rows) / len(df)) * 100 if len(df) else 0

    validity = 100  # basic placeholder, you can improve later

    return {
        "completeness": round(completeness, 2),
        "uniqueness": round(uniqueness, 2),
        "validity": round(validity, 2)
    }