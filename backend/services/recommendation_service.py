import numpy as np
import pandas as pd


class RecommendationService:

    @staticmethod
    def generate(df):

        recommendations = []

        total_rows = len(df)

        # Missing
        missing_pct = (df.isnull().sum() / total_rows) * 100

        for col, pct in missing_pct.items():
            if pct > 30:
                recommendations.append(
                    f"Column '{col}' has {pct:.1f}% missing values — consider imputation or dropping."
                )

        # Skew detection
        numeric_cols = df.select_dtypes(include=np.number)

        for col in numeric_cols.columns:
            skew = df[col].skew()
            if abs(skew) > 1:
                recommendations.append(
                    f"Column '{col}' is highly skewed — consider log transformation."
                )

        # High uniqueness (likely ID)
        for col in df.columns:
            uniqueness = df[col].nunique() / total_rows
            if uniqueness > 0.95:
                recommendations.append(
                    f"Column '{col}' has high uniqueness — likely identifier."
                )

        # High correlation warning
        if len(numeric_cols.columns) > 1:
            corr_matrix = numeric_cols.corr().abs()
            high_corr = (corr_matrix > 0.85) & (corr_matrix < 1)

            if high_corr.any().any():
                recommendations.append(
                    "Highly correlated features detected — consider feature reduction."
                )

        if not recommendations:
            recommendations.append("Dataset structure looks healthy.")

        return recommendations