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
            return ImputationEngine.impute_missing(df, n_neighbors=n_neighbors)

        return df

    # ─── simulate_cleaning ────────────────────────────────────────────────────

    @staticmethod
    def simulate_cleaning(
        df: pd.DataFrame, strategy: str, outlier_method: str = "iqr"
    ) -> dict:
        n = len(df)

        # ── Before metrics ────────────────────────────────────────────────────
        rows_before = n

        # Accuracy fix: replace common missing strings before counting
        df_norm = df.copy()
        obj_cols = df_norm.select_dtypes(include=['object']).columns
        if len(obj_cols) > 0:
            df_norm[obj_cols] = df_norm[obj_cols].apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
        df_norm.replace(['', 'NA', 'N/A', 'null', 'NULL', 'None', 'none', 'nan', '?', '-'], np.nan, inplace=True)
        
        missing_rows_before = int(df_norm.isna().all(axis=1).sum())
        missing_cells_before = int(df_norm.isna().sum().sum())
        
        total_cells = n * len(df.columns) if n else 1
        missing_pct_before = (missing_cells_before / total_cells) * 100
        
        # Duplicate count (exact)
        dup_count_before = int(df.duplicated(keep="first").sum())
        
        # Outliers on a sample
        sample_df = df if n <= 10_000 else df.sample(n=10_000, random_state=42)
        outlier_pct_before = OutlierEngine.detect_percentage(sample_df, outlier_method)

        score_before = ScoringEngine.calculate_score(
            missing_pct_before,
            (dup_count_before / n * 100) if n else 0,
            outlier_pct_before,
            0.0,
        )

        # ── Apply ─────────────────────────────────────────────────────────────
        df_clean = CleaningEngine.apply_cleaning(df.copy(), strategy)

        # ── After metrics ─────────────────────────────────────────────────────
        rows_after = len(df_clean)

        df_norm_after = df_clean.copy()
        obj_cols_a = df_norm_after.select_dtypes(include=['object']).columns
        if len(obj_cols_a) > 0:
            df_norm_after[obj_cols_a] = df_norm_after[obj_cols_a].apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
        df_norm_after.replace(['', 'NA', 'N/A', 'null', 'NULL', 'None', 'none', 'nan', '?', '-'], np.nan, inplace=True)
        
        missing_rows_after = int(df_norm_after.isna().all(axis=1).sum())
        missing_cells_after = int(df_norm_after.isna().sum().sum())
        
        total_cells_after = rows_after * len(df_clean.columns) if rows_after else 1
        missing_pct_after = (missing_cells_after / total_cells_after) * 100
        
        dup_count_after = int(df_clean.duplicated(keep="first").sum())
        
        sample_after = df_clean if rows_after <= 10_000 else df_clean.sample(n=min(10_000, rows_after), random_state=42)
        outlier_pct_after = OutlierEngine.detect_percentage(sample_after, outlier_method)

        score_after = ScoringEngine.calculate_score(
            missing_pct_after,
            (dup_count_after / rows_after * 100) if rows_after else 0,
            outlier_pct_after,
            0.0,
        )

        return {
    "rows_before": rows_before,
    "rows_after": rows_after,
    "score_before": score_before,
    "score_after": score_after,
    "improvement": round(score_after - score_before, 2),

    "missing_rows_before": missing_rows_before,
    "missing_cells_before": missing_cells_before,
    "missing_rows_after": missing_rows_after,
    "missing_cells_after": missing_cells_after,

    "missing_before": round((missing_rows_before / n * 100) if n else 0, 2),
    "missing_after": round((missing_rows_after / rows_after * 100) if rows_after else 0, 2),

    "duplicate_before": round((dup_count_before / n * 100) if n else 0, 2),
    "duplicate_after": round((dup_count_after / rows_after * 100) if rows_after else 0, 2),
    "duplicate_count_after": dup_count_after,

    "outlier_before": outlier_pct_before,
    "outlier_after": outlier_pct_after,
}