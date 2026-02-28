import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


class OutlierEngine:

    # =====================================================
    # OVERALL OUTLIER %
    # =====================================================
    @staticmethod
    def detect_percentage(df: pd.DataFrame, method: str = "iqr") -> float:

        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty or len(numeric_df) == 0:
            return 0.0

        if method == "iqr":
            mask = OutlierEngine._iqr_mask(numeric_df)
        else:
            mask = OutlierEngine._isolation_mask(numeric_df)

        return round((mask.sum() / len(numeric_df)) * 100, 2)

    # =====================================================
    # COLUMN-WISE OUTLIERS
    # =====================================================
    @staticmethod
    def detect_column_outliers(df: pd.DataFrame, method: str = "iqr"):

        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty or len(numeric_df) == 0:
            return {}

        column_outliers = {}

        if method == "iqr":

            Q1 = numeric_df.quantile(0.25)
            Q3 = numeric_df.quantile(0.75)
            IQR = Q3 - Q1

            for col in numeric_df.columns:

                # Skip constant columns
                if IQR[col] == 0:
                    column_outliers[col] = 0.0
                    continue

                lower = Q1[col] - 1.5 * IQR[col]
                upper = Q3[col] + 1.5 * IQR[col]

                mask = (numeric_df[col] < lower) | (numeric_df[col] > upper)

                percentage = (mask.sum() / len(numeric_df)) * 100
                column_outliers[col] = round(float(percentage), 2)

        else:
            # Isolation Forest applied per column independently
            for col in numeric_df.columns:

                series = numeric_df[[col]].dropna()

                if len(series) < 5:
                    column_outliers[col] = 0.0
                    continue

                model = IsolationForest(
                    contamination=0.05,
                    random_state=42
                )

                preds = model.fit_predict(series)
                mask = preds == -1

                percentage = (mask.sum() / len(series)) * 100
                column_outliers[col] = round(float(percentage), 2)

        return column_outliers

    # =====================================================
    # VISUALIZATION DATA
    # =====================================================
    @staticmethod
    def generate_outlier_chart_data(df: pd.DataFrame, method: str = "iqr"):

        column_outliers = OutlierEngine.detect_column_outliers(df, method)

        return [
            {
                "column": col,
                "outlier_percentage": value
            }
            for col, value in column_outliers.items()
        ]

    # =====================================================
    # REMOVE OUTLIERS (ROW LEVEL)
    # =====================================================
    @staticmethod
    def remove_outliers(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:

        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty or len(numeric_df) == 0:
            return df

        if method == "iqr":
            mask = OutlierEngine._iqr_mask(numeric_df)
        else:
            mask = OutlierEngine._isolation_mask(numeric_df)

        return df.loc[~mask]

    # =====================================================
    # INTERNAL METHODS
    # =====================================================
    @staticmethod
    def _iqr_mask(numeric_df: pd.DataFrame):

        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1

        mask = pd.Series(False, index=numeric_df.index)

        for col in numeric_df.columns:

            if IQR[col] == 0:
                continue

            lower = Q1[col] - 1.5 * IQR[col]
            upper = Q3[col] + 1.5 * IQR[col]

            col_mask = (numeric_df[col] < lower) | (numeric_df[col] > upper)

            mask = mask | col_mask

        return mask

    @staticmethod
    def _isolation_mask(numeric_df: pd.DataFrame):

        if len(numeric_df) < 5:
            return pd.Series([False] * len(numeric_df), index=numeric_df.index)

        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        preds = model.fit_predict(numeric_df)
        return pd.Series(preds == -1, index=numeric_df.index)