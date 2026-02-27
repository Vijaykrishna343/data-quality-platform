import pandas as pd
from engines.cleaning_engine import clean_dataframe


def clean_file(file_path: str, options: dict):

    df = pd.read_csv(file_path)

    cleaned_df = clean_dataframe(df, options)

    return cleaned_df