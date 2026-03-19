import math
import pandas as pd
import numpy as np


class ScoringEngine:

    @staticmethod
    def calculate_score(missing_pct, duplicate_pct, outlier_pct, noisy_pct):
        """
        Linear Weighted Quality Index (LWQI).
        Mathematically efficient and highly effective for data cleaning platforms.
        Provides clear, proportional lift for every error fixed.
        """
        # Ensure values are float and safe
        def safe_pct(v):
            return min(100.0, float(v or 0.0))

        m = safe_pct(missing_pct)
        d = safe_pct(duplicate_pct)
        o = safe_pct(outlier_pct)
        n = safe_pct(noisy_pct)

        # Dimensional Weights (Multiplier per 1% error)
        # Completeness is most critical (Weight 0.4 -> Multiplier 4)
        # Others are standard (Weight 0.2 -> Multiplier 2)
        penalty = (m * 4.0) + (d * 2.0) + (o * 2.0) + (n * 2.0)

        score = max(0, 100 - penalty)
        return round(score, 2)

    @staticmethod
    def calculate_metrics_and_score(df: pd.DataFrame, outlier_method: str = "iqr"):
        from backend.engines.outlier_engine import OutlierEngine
        
        total_rows = len(df)
        if total_rows == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0
            
        # 1. Missing Percentage (Row-wise: "How many rows have missing data?")
        missing_rows = df.isnull().any(axis=1).sum()
        missing_pct = (missing_rows / total_rows) * 100
        
        # 2. Duplicate Percentage (Row-wise)
        duplicate_pct = (df.duplicated().sum() / total_rows) * 100
        
        # 3. Outlier Percentage (Cell-wise: Matching Dashboard display)
        outlier_pct = OutlierEngine.detect_percentage(df, outlier_method)
        
        # 4. Noise Percentage (Cell-wise: Matching Dashboard display)
        numeric_df = df.select_dtypes(include=[np.number])
        noisy_pct = 0.0
        if not numeric_df.empty and total_rows > 1:
            means = numeric_df.mean()
            stds = numeric_df.std()
            valid_std_mask = stds > 0
            if valid_std_mask.any():
                active_numeric = numeric_df.loc[:, valid_std_mask]
                z_scores = np.abs((active_numeric - means[valid_std_mask]) / stds[valid_std_mask])
                noisy_cells = (z_scores > 3).sum().sum()
                noisy_pct = (noisy_cells / numeric_df.size) * 100
                
        score = ScoringEngine.calculate_score(missing_pct, duplicate_pct, outlier_pct, noisy_pct)
        return score, missing_pct, duplicate_pct, outlier_pct, noisy_pct


    @staticmethod
    def get_ml_readiness(score):
        """
        Unified ML readiness classification.
        """
        # NaN / None Safety
        if score is None or (isinstance(score, float) and math.isnan(score)):
            return {"status": "Not ML Ready", "level": "critical", "color": "red"}

        if score >= 94:
            return {"status": "ML Ready", "level": "high", "color": "green"}
        if score >= 80:
            return {"status": "Needs Minor Cleaning", "level": "medium", "color": "yellow"}
        if score >= 60:
            return {"status": "Needs Cleaning", "level": "low", "color": "orange"}
        return {"status": "Not ML Ready", "level": "critical", "color": "red"}

    @staticmethod
    def score_breakdown(missing_pct, duplicate_pct, outlier_pct, noisy_pct):
        """
        Returns DAMA dimension scores (0-100) for frontend visualization.
        """
        def to_score(pct):
            return round((1.0 - (min(100.0, float(pct or 0.0)) / 100.0)) * 100, 2)

        return {
            "completeness": to_score(missing_pct),
            "uniqueness": to_score(duplicate_pct),
            "accuracy": to_score(outlier_pct),
            "validity": to_score(noisy_pct),
        }