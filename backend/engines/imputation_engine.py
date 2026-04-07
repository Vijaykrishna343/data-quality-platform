import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer

class ImputationEngine:
    @staticmethod
    def impute_missing(df: pd.DataFrame, n_neighbors: int = 5) -> pd.DataFrame:
        df_imputed = df.copy()
        numeric_cols = df_imputed.select_dtypes(include=[np.number]).columns
        
        if numeric_cols.empty:
            return df_imputed

        # Optimization: Use median imputation for large datasets to avoid O(N^2) / O(N*K) KNN slow down
        if len(df_imputed) > 10000:
            for col in numeric_cols:
                if df_imputed[col].isnull().any():
                    median_val = df_imputed[col].median()
                    df_imputed[col] = df_imputed[col].fillna(median_val)
        else:
            imputer = KNNImputer(n_neighbors=n_neighbors)
            df_imputed[numeric_cols] = imputer.fit_transform(df_imputed[numeric_cols])
        
        # Categorical columns: fill with mode
        cat_cols = df_imputed.select_dtypes(exclude=[np.number]).columns
        for col in cat_cols:
            if df_imputed[col].isnull().any():
                mode_val = df_imputed[col].mode()
                fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
                df_imputed[col] = df_imputed[col].fillna(fill_val)

        return df_imputed
