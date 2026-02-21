import pandas as pd

def clean_data(df: pd.DataFrame,
               remove_duplicates=True,
               missing_strategy="median"):

    cleaned = df.copy()

    if remove_duplicates:
        cleaned = cleaned.drop_duplicates()

    for col in cleaned.columns:
        if cleaned[col].isnull().sum() > 0:
            if missing_strategy == "mean" and cleaned[col].dtype != "object":
                cleaned[col] = cleaned[col].fillna(cleaned[col].mean())
            elif missing_strategy == "median" and cleaned[col].dtype != "object":
                cleaned[col] = cleaned[col].fillna(cleaned[col].median())
            else:
                cleaned[col] = cleaned[col].fillna(cleaned[col].mode()[0])

    return cleaned