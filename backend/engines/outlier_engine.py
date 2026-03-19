import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


class OutlierEngine:

    # =====================================================
    # OVERALL OUTLIER %
    # =====================================================
    @staticmethod
    def detect_percentage(df: pd.DataFrame, method: str = "iqr") -> float:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0:
            return 0.0

        if method == "iqr" or method == "none":
            mask = OutlierEngine._iqr_cell_mask(numeric_df)
        elif method == "mad":
            mask = OutlierEngine._mad_cell_mask(numeric_df)
        else:
            # Isolation Forest is naturally row-wise, we convert to cell-ratio estimate
            row_mask = OutlierEngine._isolation_mask(numeric_df)
            return round((row_mask.sum() / len(numeric_df)) * 100, 2)

        return round((mask.sum().sum() / numeric_df.size) * 100, 2)

    # =====================================================
    # COLUMN-WISE OUTLIERS
    # =====================================================
    @staticmethod
    def detect_column_outliers(df: pd.DataFrame, method: str = "iqr"):
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0:
            return {}

        if method == "iqr":
            Q1 = numeric_df.quantile(0.25)
            Q3 = numeric_df.quantile(0.75)
            IQR = Q3 - Q1
            outliers_mask = (numeric_df < (Q1 - 1.5 * IQR)) | (numeric_df > (Q3 + 1.5 * IQR))
            percentages = (outliers_mask.sum() / len(numeric_df)) * 100
            return {col: round(float(val), 2) for col, val in percentages.items()}
        
        elif method == "mad":
            # MAD per column
            column_outliers = {}
            for col in numeric_df.columns:
                series = numeric_df[col].dropna()
                if series.empty: continue
                median = series.median()
                mad = (series - median).abs().median()
                if mad == 0:
                    column_outliers[col] = 0.0
                    continue
                # 3.5 is a standard threshold for MAD
                t_score = 0.6745 * (series - median) / mad
                mask = np.abs(t_score) > 3.5
                column_outliers[col] = round((mask.sum() / len(series)) * 100, 2)
            return column_outliers

        else:
            column_outliers = {}
            for col in numeric_df.columns:
                series = numeric_df[[col]].dropna()
                if len(series) < 5:
                    column_outliers[col] = 0.0
                    continue
                model = IsolationForest(contamination=0.05, random_state=42)
                preds = model.fit_predict(series)
                column_outliers[col] = round(((preds == -1).sum() / len(series)) * 100, 2)
            return column_outliers

    # =====================================================
    # REMOVE OUTLIERS / NOISE (ROW LEVEL)
    # =====================================================
    @staticmethod
    def remove_outliers(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0 or method == "none":
            return df

        if method == "iqr":
            mask = OutlierEngine._iqr_mask(numeric_df)
        elif method == "mad":
            mask = OutlierEngine._mad_mask(numeric_df)
        elif method == "zscore":
            mask = OutlierEngine._zscore_mask(numeric_df)
        else:
            mask = OutlierEngine._isolation_mask(numeric_df)

        return df.loc[~mask]

    # =====================================================
    # FIX OUTLIERS / NOISE (DATA IMPUTATION)
    # =====================================================
    @staticmethod
    def fix_outliers(df: pd.DataFrame, method: str = "iqr") -> pd.DataFrame:
        """
        Clamps outliers to the boundaries instead of removing rows.
        """
        df_fixed = df.copy()
        numeric_cols = df_fixed.select_dtypes(include=[np.number]).columns
        
        if numeric_cols.empty or method == "none":
            return df_fixed

        for col in numeric_cols:
            series = df_fixed[col]
            if method == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                df_fixed[col] = series.clip(lower=lower, upper=upper)
            
            elif method == "zscore" or method == "mad":
                mean = series.mean()
                std = series.std()
                if std > 0:
                    lower = mean - 3 * std
                    upper = mean + 3 * std
                    df_fixed[col] = series.clip(lower=lower, upper=upper)

        return df_fixed

    @staticmethod
    def fix_noise(df: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
        """
        Replaces noisy data points (e.g. Z-score > 3) with the median.
        """
        df_fixed = df.copy()
        numeric_cols = df_fixed.select_dtypes(include=[np.number]).columns
        
        if numeric_cols.empty or method == "none":
            return df_fixed

        for col in numeric_cols:
            series = df_fixed[col]
            mean = series.mean()
            std = series.std()
            if std > 0:
                median = series.median()
                z_scores = np.abs((series - mean) / std)
                # Replace noisy values with median
                df_fixed.loc[z_scores > 3, col] = median

        return df_fixed

    # =====================================================
    # INTERNAL MASKS (VECTORIZED)
    # =====================================================
    @staticmethod
    def _iqr_mask(numeric_df: pd.DataFrame):
        return OutlierEngine._iqr_cell_mask(numeric_df).any(axis=1)

    @staticmethod
    def _iqr_cell_mask(numeric_df: pd.DataFrame):
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        return (numeric_df < (Q1 - 1.5 * IQR)) | (numeric_df > (Q3 + 1.5 * IQR))

    @staticmethod
    def _mad_mask(numeric_df: pd.DataFrame):
        return OutlierEngine._mad_cell_mask(numeric_df).any(axis=1)

    @staticmethod
    def _mad_cell_mask(numeric_df: pd.DataFrame):
        # Multi-column MAD mask
        masks = []
        for col in numeric_df.columns:
            series = numeric_df[col]
            median = series.median()
            mad = (series - median).abs().median()
            if mad == 0:
                masks.append(pd.Series([False] * len(series), index=series.index))
            else:
                t_score = 0.6745 * (series - median) / mad
                masks.append(np.abs(t_score) > 3.5)
        return pd.concat(masks, axis=1)

    @staticmethod
    def _zscore_mask(numeric_df: pd.DataFrame):
        # Standard Z-Score > 3 (Row-wise)
        z_scores = np.abs((numeric_df - numeric_df.mean()) / numeric_df.std())
        return (z_scores > 3).any(axis=1)

    @staticmethod
    def _isolation_mask(numeric_df: pd.DataFrame):
        if len(numeric_df) < 5:
            return pd.Series([False] * len(numeric_df), index=numeric_df.index)
        model = IsolationForest(contamination=0.05, random_state=42)
        preds = model.fit_predict(numeric_df)
        return pd.Series(preds == -1, index=numeric_df.index)