import pandas as pd
import numpy as np


def remove_outliers_iqr(df: pd.DataFrame):
    numeric_columns = df.select_dtypes(include=np.number).columns

    for col in numeric_columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        df = df[(df[col] >= lower) & (df[col] <= upper)]

    return df


def clean_data(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    missing_strategy: str = "auto",
    remove_outliers: bool = True
):
    cleaned_df = df.copy()

    # ---- Remove Duplicates ----
    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates()

    # ---- Handle Missing Values ----
    for column in cleaned_df.columns:
        if cleaned_df[column].isnull().sum() == 0:
            continue

        if missing_strategy == "auto":
            if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                cleaned_df[column].fillna(cleaned_df[column].median(), inplace=True)
            else:
                cleaned_df[column].fillna(cleaned_df[column].mode()[0], inplace=True)

        elif missing_strategy == "mean":
            cleaned_df[column].fillna(cleaned_df[column].mean(), inplace=True)

        elif missing_strategy == "median":
            cleaned_df[column].fillna(cleaned_df[column].median(), inplace=True)

        elif missing_strategy == "mode":
            cleaned_df[column].fillna(cleaned_df[column].mode()[0], inplace=True)

        elif missing_strategy == "drop":
            cleaned_df = cleaned_df.dropna()

    # ---- Remove Outliers ----
    if remove_outliers:
        cleaned_df = remove_outliers_iqr(cleaned_df)

    return cleaned_df