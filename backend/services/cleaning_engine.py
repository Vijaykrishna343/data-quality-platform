import pandas as pd


def clean_dataset(df: pd.DataFrame):
    """
    Basic cleaning:
    - Drop duplicate rows
    - Fill numeric missing with median
    - Fill categorical missing with mode
    """

    original_shape = df.shape

    # Remove duplicates
    df_cleaned = df.drop_duplicates()

    # Fill missing values
    for column in df_cleaned.columns:
        if df_cleaned[column].dtype in ["int64", "float64"]:
            df_cleaned[column] = df_cleaned[column].fillna(df_cleaned[column].median())
        else:
            if not df_cleaned[column].mode().empty:
                df_cleaned[column] = df_cleaned[column].fillna(df_cleaned[column].mode()[0])

    cleaning_summary = {
        "original_rows": original_shape[0],
        "cleaned_rows": df_cleaned.shape[0],
        "duplicates_removed": original_shape[0] - df_cleaned.shape[0]
    }

    return df_cleaned, cleaning_summary