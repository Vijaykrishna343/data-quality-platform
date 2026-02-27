import pandas as pd

class ImportanceEngine:

    @staticmethod
    def calculate(df: pd.DataFrame):

        total_rows = len(df)
        importance_scores = {}

        for col in df.columns:

            missing_ratio = df[col].isnull().mean()

            unique_ratio = (
                df[col].nunique() / total_rows
                if total_rows > 0 else 0
            )

            # Detect identifier column
            is_identifier = unique_ratio > 0.95

            # Weighted formula
            score = (
                (1 - missing_ratio) * 40 +
                unique_ratio * 40 +
                (0 if is_identifier else 20)
            )

            # Cap score
            if score > 95:
                score = 95

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