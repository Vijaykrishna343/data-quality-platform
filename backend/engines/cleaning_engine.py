"""
Cleaning Engine — Optimised
============================
Key improvements:
• Fuzzy duplicate detection is SKIPPED for > 50 k rows (exact match only).
• KNN imputation is SKIPPED for > 10 k rows (median/mode fallback).
• simulate_cleaning avoids full DataFrame copies where possible.
• All duplicate checks use vectorised pandas instead of per-row loops.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine

# Thresholds for algorithm switching
_KNN_MAX_ROWS  = 10_000
_FUZZY_MAX_ROWS = 50_000


class CleaningEngine:

    # ─── apply_cleaning ───────────────────────────────────────────────────────

    @staticmethod
    def apply_cleaning(df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        n = len(df)

        if strategy == "drop_missing":
            return df.dropna()

        if strategy == "remove_duplicates":
            if n > _FUZZY_MAX_ROWS:
                # Exact match only for large datasets (fuzzy is O(N²))
                return df.drop_duplicates(keep="first")
            from backend.engines.duplicate_engine import DuplicateEngine
            return DuplicateEngine.remove_fuzzy_duplicates(
                df, list(df.columns), threshold=90.0
            )

        if strategy == "remove_both":
            df = df.dropna()
            if len(df) > _FUZZY_MAX_ROWS:
                return df.drop_duplicates(keep="first")
            from backend.engines.duplicate_engine import DuplicateEngine
            return DuplicateEngine.remove_fuzzy_duplicates(
                df, list(df.columns), threshold=90.0
            )

        if strategy in ("fill_mean", "fill_mode"):
            from backend.engines.imputation_engine import ImputationEngine
            n_neighbors = 5 if strategy == "fill_mean" else 3
            # ImputationEngine already switches to median for > 10 k rows
            return ImputationEngine.impute_missing(df, n_neighbors=n_neighbors)

        return df

    # ─── simulate_cleaning ────────────────────────────────────────────────────

    @staticmethod
    def simulate_cleaning(
        df: pd.DataFrame, strategy: str, outlier_method: str = "iqr"
    ) -> dict:
        n = len(df)

        # ── Before metrics ────────────────────────────────────────────────────
        rows_before         = n
        missing_ratio_before = df.isnull().mean().mean()

        # Fast duplicate ratio — exact match (vectorised)
        dup_count_before    = int(df.duplicated(keep="first").sum())
        duplicate_ratio_before = dup_count_before / n if n else 0

        # Outliers on a sample for speed
        sample_df           = df if n <= 10_000 else df.sample(n=10_000, random_state=42)
        outlier_pct_before  = OutlierEngine.detect_percentage(sample_df, outlier_method)

        score_before = ScoringEngine.calculate_score(
            missing_ratio_before * 100,
            duplicate_ratio_before * 100,
            outlier_pct_before,
            0.0,
        )

        # ── Apply ─────────────────────────────────────────────────────────────
        df_clean = CleaningEngine.apply_cleaning(df.copy(), strategy)

        # ── After metrics ─────────────────────────────────────────────────────
        rows_after          = len(df_clean)
        missing_ratio_after  = df_clean.isnull().mean().mean()
        dup_count_after     = int(df_clean.duplicated(keep="first").sum())
        duplicate_ratio_after = dup_count_after / rows_after if rows_after else 0

        sample_after        = (
            df_clean if rows_after <= 10_000
            else df_clean.sample(n=10_000, random_state=42)
        )
        outlier_pct_after   = OutlierEngine.detect_percentage(sample_after, outlier_method)

        score_after = ScoringEngine.calculate_score(
            missing_ratio_after * 100,
            duplicate_ratio_after * 100,
            outlier_pct_after,
            0.0,
        )

        return {
            "rows_before":       rows_before,
            "rows_after":        rows_after,
            "score_before":      score_before,
            "score_after":       score_after,
            "improvement":       round(score_after - score_before, 2),
            "missing_before":    round(missing_ratio_before * 100, 2),
            "missing_after":     round(missing_ratio_after * 100, 2),
            "duplicate_before":  round(duplicate_ratio_before * 100, 2),
            "duplicate_after":   round(duplicate_ratio_after * 100, 2),
            "outlier_before":    outlier_pct_before,
            "outlier_after":     outlier_pct_after,
        }