import numpy as np
import pandas as pd
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine


class CleaningEngine:

    @staticmethod
    def apply_cleaning(df: pd.DataFrame, strategy: str):

        if strategy == "drop_missing":
            df = df.dropna()

        elif strategy == "remove_duplicates":
            from backend.engines.duplicate_engine import DuplicateEngine
            df = DuplicateEngine.remove_fuzzy_duplicates(df, list(df.columns), threshold=90.0)

        elif strategy == "remove_both":
            from backend.engines.duplicate_engine import DuplicateEngine
            df = df.dropna()
            df = DuplicateEngine.remove_fuzzy_duplicates(df, list(df.columns), threshold=90.0)

        elif strategy == "fill_mean":
            from backend.engines.imputation_engine import ImputationEngine
            # using KNN Imputer instead of mean
            df = ImputationEngine.impute_missing(df, n_neighbors=5)

        elif strategy == "fill_mode":
            from backend.engines.imputation_engine import ImputationEngine
            # using KNN Imputer instead of mode
            df = ImputationEngine.impute_missing(df, n_neighbors=3)

        return df

    @staticmethod
    def simulate_cleaning(df: pd.DataFrame, strategy: str, outlier_method: str = "iqr"):

        df_copy = df.copy()

        rows_before = len(df)
        missing_ratio_before = df.isnull().mean().mean()
        from backend.engines.duplicate_engine import DuplicateEngine
        dup_indices_before = DuplicateEngine.detect_fuzzy_duplicates(df, list(df.columns), threshold=95.0)
        duplicate_ratio_before = len(dup_indices_before) / rows_before if rows_before else 0

        outlier_percent_before = OutlierEngine.detect_percentage(df, outlier_method)

        score_before = ScoringEngine.calculate_score(
            missing_ratio_before * 100,
            duplicate_ratio_before * 100,
            outlier_percent_before,
            0.0 # noisy_pct
        )

        df_copy = CleaningEngine.apply_cleaning(df_copy, strategy)

        rows_after = len(df_copy)
        missing_ratio_after = df_copy.isnull().mean().mean()
        from backend.engines.duplicate_engine import DuplicateEngine
        dup_indices_after = DuplicateEngine.detect_fuzzy_duplicates(df_copy, list(df_copy.columns), threshold=95.0)
        duplicate_ratio_after = len(dup_indices_after) / len(df_copy) if len(df_copy) else 0

        outlier_percent_after = OutlierEngine.detect_percentage(df_copy, outlier_method)

        score_after = ScoringEngine.calculate_score(
            missing_ratio_after * 100,
            duplicate_ratio_after * 100,
            outlier_percent_after,
            0.0 # noisy_pct
        )

        return {
            "rows_before": rows_before,
            "rows_after": rows_after,
            "score_before": score_before,
            "score_after": score_after,
            "improvement": round(score_after - score_before, 2),
            "missing_before": round(missing_ratio_before * 100, 2),
            "missing_after": round(missing_ratio_after * 100, 2),
            "duplicate_before": round(duplicate_ratio_before * 100, 2),
            "duplicate_after": round(duplicate_ratio_after * 100, 2),
            "outlier_before": outlier_percent_before,
            "outlier_after": outlier_percent_after
        }