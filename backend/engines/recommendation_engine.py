import pandas as pd
import numpy as np


class RecommendationEngine:

    @staticmethod
    def analyze(df: pd.DataFrame):

        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols

        recommendations = []

        # ================= MISSING VALUES =================
        for col in df.columns:
            missing_ratio = df[col].isnull().mean()

            if missing_ratio > 0.3:
                recommendations.append({
                    "column": col,
                    "issue": "High Missing Values",
                    "percentage": round(missing_ratio * 100, 2),
                    "suggestion": "Consider dropping this column"
                })
            elif missing_ratio > 0.05:
                recommendations.append({
                    "column": col,
                    "issue": "Moderate Missing Values",
                    "percentage": round(missing_ratio * 100, 2),
                    "suggestion": "Use mean/median imputation"
                })

        # ================= HIGH UNIQUENESS =================
        for col in df.columns:
            unique_ratio = df[col].nunique() / total_rows

            if unique_ratio > 0.95:
                recommendations.append({
                    "column": col,
                    "issue": "High Uniqueness",
                    "percentage": round(unique_ratio * 100, 2),
                    "suggestion": "Likely identifier column"
                })

        # ================= SKEW DETECTION =================
        numeric_cols = df.select_dtypes(include=np.number).columns

        for col in numeric_cols:
            skewness = df[col].skew()

            if abs(skewness) > 1:
                recommendations.append({
                    "column": col,
                    "issue": "Highly Skewed",
                    "value": round(skewness, 2),
                    "suggestion": "Consider log transformation"
                })

        # ================= DUPLICATE CHECK =================
        duplicate_ratio = df.duplicated().mean()

        if duplicate_ratio > 0.05:
            recommendations.append({
                "column": "Dataset Level",
                "issue": "High Duplicate Rows",
                "percentage": round(duplicate_ratio * 100, 2),
                "suggestion": "Remove duplicate rows"
            })

        return recommendations