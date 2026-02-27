import pandas as pd
import numpy as np


class ProfilingEngine:

    @staticmethod
    def generate_profile(df: pd.DataFrame):
        """
        Generate complete dataset profile
        """

        rows = len(df)
        columns = len(df.columns)

        # Missing values
        total_missing = df.isnull().sum().sum()
        total_cells = rows * columns if rows * columns > 0 else 1
        missing_ratio = total_missing / total_cells

        # Duplicate rows
        duplicate_count = df.duplicated().sum()
        duplicate_ratio = duplicate_count / rows if rows > 0 else 0

        # Data type breakdown
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        categorical_columns = df.select_dtypes(
            exclude=np.number
        ).columns.tolist()

        data_types = {
            "numeric_count": len(numeric_columns),
            "categorical_count": len(categorical_columns),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns
        }

        # Correlation matrix
        correlation = {}
        numeric_df = df.select_dtypes(include=np.number)

        if not numeric_df.empty:
            correlation = (
                numeric_df.corr()
                .round(2)
                .fillna(0)
                .to_dict()
            )

        return {
            "rows": rows,
            "columns": columns,
            "missing_ratio": round(missing_ratio, 4),
            "duplicate_ratio": round(duplicate_ratio, 4),
            "duplicate_count": int(duplicate_count),
            "data_types": data_types,
            "correlation": correlation
        }