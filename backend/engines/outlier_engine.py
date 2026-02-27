import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


class OutlierEngine:

    # ================= OVERALL OUTLIER % =================
    @staticmethod
    def detect_percentage(df: pd.DataFrame, method: str = "iqr") -> float:
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            return 0.0

        if method == "iqr":
            mask = OutlierEngine._iqr_mask(numeric_df)
        else:
            mask = OutlierEngine._isolation_mask(numeric_df)

        outlier_rows = mask.sum()
        total_rows = len(df)

        if total_rows == 0:
            return 0.0

        return round((outlier_rows / total_rows) * 100, 2)

    # ================= COLUMN-WISE OUTLIERS =================
    @staticmethod
    def detect_column_outliers(df: pd.DataFrame, method: str = "iqr"):
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            return {}

        column_outliers = {}

        if method == "iqr":
            Q1 = numeric_df.quantile(0.25)
            Q3 = numeric_df.quantile(0.75)
            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            for col in numeric_df.columns:
                mask = (numeric_df[col] < lower[col]) | (
                    numeric_df[col] > upper[col]
                )

                percentage = (mask.sum() / len(df)) * 100
                column_outliers[col] = round(percentage, 2)

        else:
            model = IsolationForest(
                contamination=0.05,
                random_state=42
            )
            preds = model.fit_predict(numeric_df)
            mask = preds == -1

            percentage = (mask.sum() / len(df)) * 100

            for col in numeric_df.columns:
                column_outliers[col] = round(percentage, 2)

        return column_outliers

    # ================= VISUALIZATION DATA =================
    @staticmethod
    def generate_outlier_chart_data(df: pd.DataFrame, method: str = "iqr"):
        column_outliers = OutlierEngine.detect_column_outliers(df, method)

        chart_data = []

        for col, value in column_outliers.items():
            chart_data.append({
                "column": col,
                "outlier_percentage": value
            })

        return chart_data

    # ================= REMOVE OUTLIERS =================
    @staticmethod
    def remove_outliers(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            return df

        if method == "iqr":
            mask = OutlierEngine._iqr_mask(numeric_df)
        else:
            mask = OutlierEngine._isolation_mask(numeric_df)

        return df[~mask]

    # ================= INTERNAL METHODS =================
    @staticmethod
    def _iqr_mask(numeric_df: pd.DataFrame):
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        mask = ((numeric_df < lower) | (numeric_df > upper)).any(axis=1)
        return mask

    @staticmethod
    def _isolation_mask(numeric_df: pd.DataFrame):
        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )
        preds = model.fit_predict(numeric_df)
        return preds == -1