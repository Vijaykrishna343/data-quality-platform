import pandas as pd
import numpy as np


def detect_outliers_iqr(df: pd.DataFrame):
    outlier_count = 0

    numeric_columns = df.select_dtypes(include=np.number).columns

    for col in numeric_columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_count += len(outliers)

    return int(outlier_count)


def profile_data(df: pd.DataFrame):
    rows = df.shape[0]
    columns = df.shape[1]

    missing_total = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    outlier_count = detect_outliers_iqr(df)

    completeness_ratio = 1 - (missing_total / (rows * columns)) if rows * columns > 0 else 1

    return {
        "rows": rows,
        "columns": columns,
        "missing_values": missing_total,
        "duplicate_rows": duplicate_rows,
        "outlier_count": outlier_count,
        "completeness_ratio": completeness_ratio
    }