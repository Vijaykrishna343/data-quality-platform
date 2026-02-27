import pandas as pd
import numpy as np


class ClassificationEngine:

    @staticmethod
    def classify(df: pd.DataFrame):

        classification = {
            "numeric": [],
            "categorical": [],
            "alphanumeric": [],
            "boolean": [],
            "identifier": [],
            "datetime": [],
            "text": []
        }

        total_rows = len(df)

        for col in df.columns:

            series = df[col]

            # Boolean
            if series.dropna().isin([0, 1, True, False]).all():
                classification["boolean"].append(col)
                continue

            # Numeric
            if pd.api.types.is_numeric_dtype(series):
                classification["numeric"].append(col)
                continue

            # Datetime
            try:
                pd.to_datetime(series.dropna().iloc[:5])
                classification["datetime"].append(col)
                continue
            except:
                pass

            # High uniqueness → Identifier
            unique_ratio = series.nunique() / total_rows
            if unique_ratio > 0.95:
                classification["identifier"].append(col)
                continue

            # Alphanumeric
            if series.dropna().astype(str).str.contains(r"[a-zA-Z]").any() and \
               series.dropna().astype(str).str.contains(r"[0-9]").any():
                classification["alphanumeric"].append(col)
                continue

            # Text (long strings)
            avg_len = series.dropna().astype(str).str.len().mean()
            if avg_len and avg_len > 30:
                classification["text"].append(col)
                continue

            # Default → categorical
            classification["categorical"].append(col)

        return classification