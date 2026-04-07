import math
import pandas as pd
import numpy as np


class ScoringEngine:
    # Weighted Scoring Constants for Maintainability
    WEIGHT_COMPLETENESS = 0.35  # (1-missing_pct)
    WEIGHT_UNIQUENESS    = 0.25  # (1-duplicate_pct)
    WEIGHT_CONSISTENCY   = 0.20  # (1-noisy_pct)
    WEIGHT_ACCURACY      = 0.20  # (1-outlier_pct)

    SCORE_CAP = 98.0

    @staticmethod
    def calculate_score(missing_pct: float, duplicate_pct: float, outlier_pct: float, noisy_pct: float) -> float:
        """
        Unified weighted formula for Data Quality Score.
        Q = 0.35*C + 0.25*U + 0.20*S + 0.20*(100 - O)
        """
        def safe_pct(v):
            return min(100.0, max(0.0, float(v or 0.0)))

        m = safe_pct(missing_pct)
        d = safe_pct(duplicate_pct)
        o = safe_pct(outlier_pct)
        n = safe_pct(noisy_pct)

        # Component Metrics
        c = 100.0 - m  # Completeness
        u = 100.0 - d  # Uniqueness
        s = 100.0 - n  # Consistency (Noisy Data)
        
        # Weighted Scoring Logic
        score = (
            (ScoringEngine.WEIGHT_COMPLETENESS * c) +
            (ScoringEngine.WEIGHT_UNIQUENESS    * u) +
            (ScoringEngine.WEIGHT_CONSISTENCY   * s) +
            (ScoringEngine.WEIGHT_ACCURACY      * (100.0 - o))
        )

        # Apply Realistic Score Cap
        final_score = min(score, ScoringEngine.SCORE_CAP)
        
        return round(final_score, 2)

    @staticmethod
    def calculate_metrics_and_score(df: pd.DataFrame, outlier_method: str = "iqr"):
        from backend.engines.outlier_engine import OutlierEngine
        from backend.engines.duplicate_engine import DuplicateEngine
        
        total_rows = len(df)
        if total_rows == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0
            
        # Optimized Missing Value Calculation (Vectorized)
        missing_rows = df.isna().any(axis=1).sum()
        missing_pct = (missing_rows / total_rows) * 100
        
        # Fuzzy duplicates are already optimized in DuplicateEngine (with sampling)
        dup_indices = DuplicateEngine.detect_fuzzy_duplicates(df, list(df.columns), threshold=95.0)
        duplicate_pct = (len(dup_indices) / total_rows) * 100
        
        # Outlier detection (vectorized inside OutlierEngine)
        outlier_pct = OutlierEngine.detect_percentage(df, outlier_method)
        
        # Vectorized Noisy Data Detection (Z-Score > 3)
        numeric_df = df.select_dtypes(include=[np.number])
        noisy_pct = 0.0
        if not numeric_df.empty and total_rows > 1:
            # Vectorized z-score calculation across all numeric columns
            # We use handles for means and stds to avoid repeated computation
            means = numeric_df.mean()
            stds = numeric_df.std()
            
            # Filter columns with 0 variance to avoid division by zero
            valid_cols = stds[stds > 0].index
            if not valid_cols.empty:
                active_df = numeric_df[valid_cols]
                z_scores = (active_df - means[valid_cols]) / stds[valid_cols]
                noisy_cells = (np.abs(z_scores) > 3).values.sum()
                noisy_pct = (noisy_cells / numeric_df.size) * 100
                
        score = ScoringEngine.calculate_score(missing_pct, duplicate_pct, outlier_pct, noisy_pct)
        return score, missing_pct, duplicate_pct, outlier_pct, noisy_pct

    @staticmethod
    def get_ml_readiness(score):
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
        def to_score(pct):
            return round((1.0 - (min(100.0, float(pct or 0.0)) / 100.0)) * 100, 2)

        return {
            "completeness": to_score(missing_pct),
            "uniqueness": to_score(duplicate_pct),
            "accuracy": to_score(outlier_pct),
            "validity": to_score(noisy_pct),
        }