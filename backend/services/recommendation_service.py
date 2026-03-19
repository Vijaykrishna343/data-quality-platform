import numpy as np
import pandas as pd


class RecommendationService:

    @staticmethod
    def generate(df):
        recommendations = []
        total_rows = len(df)
        if total_rows == 0:
            return []

        # 1. Missing Values (Critical/Warning)
        missing_counts = df.isnull().sum()
        for col, count in missing_counts.items():
            pct = (count / total_rows) * 100
            if pct > 40:
                recommendations.append({
                    "level": "critical",
                    "category": "High Data Loss",
                    "column": col,
                    "insight": f"Column '{col}' is missing {pct:.1f}% of its data.",
                    "action": "Consider dropping this column or performing heavy imputation."
                })
            elif pct > 10:
                recommendations.append({
                    "level": "warning",
                    "category": "Missing Data",
                    "column": col,
                    "insight": f"Column '{col}' has {pct:.1f}% gaps.",
                    "action": "Use mean/median/mode imputation to fill the gaps."
                })

        # 2. Skewness (Warning)
        numeric_cols = df.select_dtypes(include=np.number).columns
        for col in numeric_cols:
            skew = df[col].skew()
            if abs(skew) > 1.5:
                recommendations.append({
                    "level": "warning",
                    "category": "Data Distribution",
                    "column": col,
                    "insight": f"'{col}' is highly skewed ({skew:.2f}).",
                    "action": "Apply a Log or Box-Cox transformation to normalize the scale."
                })

        # 3. High Uniqueness / IDs (Info)
        for col in df.columns:
            uniqueness = df[col].nunique() / total_rows
            if uniqueness > 0.98 and total_rows > 10:
                recommendations.append({
                    "level": "info",
                    "category": "Identifier Detection",
                    "column": col,
                    "insight": f"'{col}' has nearly 100% unique values.",
                    "action": "Usually an ID column. Exclude it from ML training."
                })

        # 4. Multi-collinearity (Warning)
        if len(numeric_cols) > 1:
            numeric_df = df[numeric_cols].select_dtypes(include=[np.number])
            if numeric_df.shape[1] > 1:
                corr_matrix = numeric_df.corr().abs()
                upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                high_corr_cols = [column for column in upper.columns if any(upper[column] > 0.90)]
                
                if high_corr_cols:
                    recommendations.append({
                        "level": "warning",
                        "category": "Redundancy",
                        "column": ", ".join(high_corr_cols[:2]),
                        "insight": "Highly correlated features detected.",
                        "action": "Perform feature reduction or drop one of the redundant columns."
                    })

        if not recommendations:
            recommendations.append({
                "level": "info",
                "category": "Stability",
                "column": "Dataset",
                "insight": "No critical quality issues found.",
                "action": "Proceed with analysis or model training."
            })

        return recommendations