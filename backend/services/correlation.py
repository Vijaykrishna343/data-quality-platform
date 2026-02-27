import pandas as pd


def calculate_correlation(file_path: str):

    df = pd.read_csv(file_path)
    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        return {}

    return numeric_df.corr().fillna(0).to_dict()