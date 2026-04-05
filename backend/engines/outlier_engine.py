import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class OutlierEngine:

    @staticmethod
    def detect_percentage(df: pd.DataFrame, method: str = "hybrid") -> float:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0:
            return 0.0

        if method == "iqr":
            mask = OutlierEngine._iqr_cell_mask(numeric_df).any(axis=1)
        elif method == "mad":
            mask = OutlierEngine._mad_cell_mask(numeric_df).any(axis=1)
        elif method == "lof":
            mask = OutlierEngine._lof_mask(numeric_df)
        elif method == "if":
            mask = OutlierEngine._isolation_mask(numeric_df)
        else: # Hybrid
            mask = OutlierEngine._hybrid_mask(numeric_df)

        return round((mask.sum() / len(numeric_df)) * 100, 2)

    @staticmethod
    def detect_column_outliers(df: pd.DataFrame, method: str = "hybrid") -> dict:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0:
            return {}

        column_outliers = {}
        for col in numeric_df.columns:
            single_col_df = numeric_df[[col]]
            if method == "iqr":
                mask = OutlierEngine._iqr_cell_mask(single_col_df).any(axis=1)
            elif method == "mad":
                mask = OutlierEngine._mad_cell_mask(single_col_df).any(axis=1)
            elif method == "lof":
                mask = OutlierEngine._lof_mask(single_col_df)
            elif method == "if":
                mask = OutlierEngine._isolation_mask(single_col_df)
            else:
                mask = OutlierEngine._hybrid_mask(single_col_df)

            outliers_count = mask.sum()
            if outliers_count > 0:
                column_outliers[col] = round((outliers_count / len(numeric_df)) * 100, 2)
        
        return dict(sorted(column_outliers.items(), key=lambda item: item[1], reverse=True))


    @staticmethod
    def _hybrid_mask(numeric_df: pd.DataFrame):
        if len(numeric_df) < 5:
            return pd.Series([False] * len(numeric_df), index=numeric_df.index)
        
        # Fill missing values strictly for the models
        filled_df = numeric_df.fillna(numeric_df.median())
        
        # Isolation Forest
        if_model = IsolationForest(contamination=0.05, random_state=42)
        if_preds = if_model.fit_predict(filled_df)
        
        # Local Outlier Factor
        lof_model = LocalOutlierFactor(n_neighbors=min(20, len(filled_df)-1), contamination=0.05)
        lof_preds = lof_model.fit_predict(filled_df)
        
        # Hybrid: if EITHER says outlier (-1)
        return pd.Series((if_preds == -1) | (lof_preds == -1), index=numeric_df.index)

    @staticmethod
    def _isolation_mask(numeric_df: pd.DataFrame):
        if len(numeric_df) < 5:
            return pd.Series([False] * len(numeric_df), index=numeric_df.index)
        filled_df = numeric_df.fillna(numeric_df.median())
        model = IsolationForest(contamination=0.05, random_state=42)
        preds = model.fit_predict(filled_df)
        return pd.Series(preds == -1, index=numeric_df.index)

    @staticmethod
    def _lof_mask(numeric_df: pd.DataFrame):
        if len(numeric_df) < 5:
            return pd.Series([False] * len(numeric_df), index=numeric_df.index)
        filled_df = numeric_df.fillna(numeric_df.median())
        model = LocalOutlierFactor(n_neighbors=min(20, len(filled_df)-1), contamination=0.05)
        preds = model.fit_predict(filled_df)
        return pd.Series(preds == -1, index=numeric_df.index)

    @staticmethod
    def _iqr_cell_mask(numeric_df: pd.DataFrame):
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        return (numeric_df < (Q1 - 1.5 * IQR)) | (numeric_df > (Q3 + 1.5 * IQR))

    @staticmethod
    def _mad_cell_mask(numeric_df: pd.DataFrame):
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
        if not masks:
             return pd.DataFrame()
        return pd.concat(masks, axis=1)

    @staticmethod
    def remove_outliers(df: pd.DataFrame, method: str = "hybrid") -> pd.DataFrame:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df) == 0 or method == "none":
            return df

        if method == "iqr":
            mask = OutlierEngine._iqr_cell_mask(numeric_df).any(axis=1)
        elif method == "mad":
            mask = OutlierEngine._mad_cell_mask(numeric_df).any(axis=1)
        elif method == "lof":
            mask = OutlierEngine._lof_mask(numeric_df)
        elif method == "hybrid":
            mask = OutlierEngine._hybrid_mask(numeric_df)
        else:
            mask = OutlierEngine._isolation_mask(numeric_df)

        return df.loc[~mask]

    @staticmethod
    def fix_outliers(df: pd.DataFrame, method: str = "hybrid") -> pd.DataFrame:
        # Instead of removal, we clamp using IQR or Z-score for all since hybrid targets rows.
        # So we default to IQR clipping.
        df_fixed = df.copy()
        numeric_cols = df_fixed.select_dtypes(include=[np.number]).columns
        
        if numeric_cols.empty or method == "none":
            return df_fixed

        for col in numeric_cols:
            series = df_fixed[col]
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df_fixed[col] = series.clip(lower=lower, upper=upper)

        return df_fixed

    @staticmethod
    def fix_noise(df: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
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
                df_fixed.loc[z_scores > 3, col] = median

        return df_fixed