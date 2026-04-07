"""
Outlier Engine — Optimised
==========================
Key improvements:
• detect_percentage / detect_column_outliers auto-sample large datasets
  for expensive methods (LOF, Isolation Forest, Hybrid).
• IQR and MAD are fully vectorised and run on the full dataset.
• _hybrid_mask uses a sample-safe guard (≤ SAMPLE_CAP rows sent to sklearn).
• fix_outliers / fix_noise remain vectorised (clip / where).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

SAMPLE_CAP = 10_000                            # max rows sent to ML-based detectors
_ML_METHODS = {"lof", "if", "hybrid", "isolation_forest"}


class OutlierEngine:

    # ── Public API ────────────────────────────────────────────────────────────

    @staticmethod
    def detect_percentage(df: pd.DataFrame, method: str = "hybrid") -> float:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0:
            return 0.0

        # Sample for expensive methods
        work_df = OutlierEngine._maybe_sample(numeric_df, method)
        mask    = OutlierEngine._row_mask(work_df, method)
        return round((mask.sum() / len(work_df)) * 100, 2)

    @staticmethod
    def detect_column_outliers(df: pd.DataFrame, method: str = "hybrid") -> dict:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0:
            return {}

        work_df        = OutlierEngine._maybe_sample(numeric_df, method)
        column_outliers = {}
        for col in work_df.columns:
            single = work_df[[col]]
            mask   = OutlierEngine._row_mask(single, method)
            count  = mask.sum()
            if count > 0:
                column_outliers[col] = round((count / len(work_df)) * 100, 2)

        return dict(sorted(column_outliers.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def remove_outliers(df: pd.DataFrame, method: str = "hybrid") -> pd.DataFrame:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0 or method == "none":
            return df
        work_df = OutlierEngine._maybe_sample(numeric_df, method)
        mask    = OutlierEngine._row_mask(work_df, method)

        # If we sampled, only drop rows that are in the sample AND flagged
        if len(work_df) < len(df):
            flagged_idx = work_df.index[mask]
            return df.drop(index=flagged_idx)
        return df.loc[~mask]

    @staticmethod
    def fix_outliers(df: pd.DataFrame, method: str = "none") -> pd.DataFrame:
        if method == "none":
            return df
        df_fixed     = df.copy()
        numeric_cols = df_fixed.select_dtypes(include=[np.number]).columns
        if numeric_cols.empty:
            return df_fixed

        # Vectorised clipping
        Q1    = df_fixed[numeric_cols].quantile(0.25)
        Q3    = df_fixed[numeric_cols].quantile(0.75)
        IQR   = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df_fixed[numeric_cols] = df_fixed[numeric_cols].clip(lower=lower, upper=upper, axis=1)
        return df_fixed

    @staticmethod
    def fix_noise(df: pd.DataFrame, method: str = "none") -> pd.DataFrame:
        if method == "none":
            return df
        df_fixed     = df.copy()
        numeric_cols = df_fixed.select_dtypes(include=[np.number]).columns
        if numeric_cols.empty:
            return df_fixed

        # Vectorised Z-Score noise fix
        means   = df_fixed[numeric_cols].mean()
        stds    = df_fixed[numeric_cols].std()
        medians = df_fixed[numeric_cols].median()

        valid = stds[stds > 0].index
        if not valid.empty:
            z = (df_fixed[valid] - means[valid]) / stds[valid]
            noisy = z.abs() > 3
            df_fixed[valid] = df_fixed[valid].where(~noisy, medians[valid], axis=1)
        return df_fixed

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _maybe_sample(numeric_df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Down-sample large frames when using ML-based detectors."""
        if method in _ML_METHODS and len(numeric_df) > SAMPLE_CAP:
            return numeric_df.sample(n=SAMPLE_CAP, random_state=42)
        return numeric_df

    @staticmethod
    def _row_mask(numeric_df: pd.DataFrame, method: str) -> pd.Series:
        """Return a boolean Series flagging outlier rows."""
        if method == "iqr":
            return OutlierEngine._iqr_cell_mask(numeric_df).any(axis=1)
        if method == "mad":
            return OutlierEngine._mad_cell_mask(numeric_df).any(axis=1)
        if method == "lof":
            return OutlierEngine._lof_mask(numeric_df)
        if method in ("if", "isolation_forest"):
            return OutlierEngine._isolation_mask(numeric_df)
        # hybrid (default)
        return OutlierEngine._hybrid_mask(numeric_df)

    # ── Masks ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _hybrid_mask(numeric_df: pd.DataFrame) -> pd.Series:
        if len(numeric_df) < 5:
            return pd.Series(False, index=numeric_df.index)
        filled = numeric_df.fillna(numeric_df.median())

        if_model  = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
        if_preds  = if_model.fit_predict(filled)

        n_neighbors = min(20, len(filled) - 1)
        lof_model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.05, n_jobs=-1)
        lof_preds = lof_model.fit_predict(filled)

        return pd.Series((if_preds == -1) | (lof_preds == -1), index=numeric_df.index)

    @staticmethod
    def _isolation_mask(numeric_df: pd.DataFrame) -> pd.Series:
        if len(numeric_df) < 5:
            return pd.Series(False, index=numeric_df.index)
        filled = numeric_df.fillna(numeric_df.median())
        model  = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
        preds  = model.fit_predict(filled)
        return pd.Series(preds == -1, index=numeric_df.index)

    @staticmethod
    def _lof_mask(numeric_df: pd.DataFrame) -> pd.Series:
        if len(numeric_df) < 5:
            return pd.Series(False, index=numeric_df.index)
        filled = numeric_df.fillna(numeric_df.median())
        n_neighbors = min(20, len(filled) - 1)
        model  = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.05, n_jobs=-1)
        preds  = model.fit_predict(filled)
        return pd.Series(preds == -1, index=numeric_df.index)

    @staticmethod
    def _iqr_cell_mask(numeric_df: pd.DataFrame) -> pd.DataFrame:
        Q1  = numeric_df.quantile(0.25)
        Q3  = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        return (numeric_df < (Q1 - 1.5 * IQR)) | (numeric_df > (Q3 + 1.5 * IQR))

    @staticmethod
    def _mad_cell_mask(numeric_df: pd.DataFrame) -> pd.DataFrame:
        medians  = numeric_df.median()
        abs_diff = (numeric_df - medians).abs()
        mads     = abs_diff.median()

        valid    = mads[mads > 0].index
        mask_df  = pd.DataFrame(False, index=numeric_df.index, columns=numeric_df.columns)
        if not valid.empty:
            t_scores = 0.6745 * (numeric_df[valid] - medians[valid]) / mads[valid]
            mask_df[valid] = t_scores.abs() > 3.5
        return mask_df