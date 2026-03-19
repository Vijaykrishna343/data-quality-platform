import pandas as pd


class CompletenessEngine:

    @staticmethod
    def calculate(df: pd.DataFrame) -> float:
        total_cells = len(df) * len(df.columns)

        if total_cells == 0:
            return 0.0

        total_missing = df.isna().sum().sum()

        completeness = (1 - (total_missing / total_cells)) * 100

        return round(float(completeness), 2)