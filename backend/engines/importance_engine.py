import pandas as pd
import numpy as np


class ImportanceEngine:

    @staticmethod
    def calculate(df: pd.DataFrame):

        total_rows = len(df)

        if total_rows == 0:
            return {}

        importance_scores = {}

        for col in df.columns:

            series = df[col]

            # =====================
            # Missing Ratio
            # =====================
            missing_ratio = series.isnull().mean()

            # =====================
            # Unique Ratio
            # =====================
            unique_count = series.nunique(dropna=True)
            unique_ratio = unique_count / total_rows if total_rows > 0 else 0

            # =====================
            # Detect Identifier
            # =====================
            is_identifier = unique_ratio > 0.95

            # =====================
            # Detect Constant Column
            # =====================
            is_constant = unique_count <= 1

            # =====================
            # Data Type Weight
            # =====================
            if pd.api.types.is_numeric_dtype(series):
                dtype_weight = 15
            else:
                dtype_weight = 10

            # =====================
            # Variance Bonus (numeric only)
            # =====================
            variance_bonus = 0
            if pd.api.types.is_numeric_dtype(series) and not is_constant:
                variance = series.var()
                if variance > 0:
                    variance_bonus = 10

            # =====================
            # Base Score Formula
            # =====================
            score = (
                (1 - missing_ratio) * 40 +   # completeness weight
                unique_ratio * 25 +          # uniqueness weight
                dtype_weight +               # type usefulness
                variance_bonus               # numeric usefulness
            )

            # Penalize identifier columns
            if is_identifier:
                score -= 20

            # Penalize constant columns
            if is_constant:
                score -= 30

            # =====================
            # Clamp score
            # =====================
            score = max(0, min(score, 95))

            importance_scores[col] = round(score, 2)

        # Sort descending
        sorted_scores = dict(
            sorted(
                importance_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

        return sorted_scores