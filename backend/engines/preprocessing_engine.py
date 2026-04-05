import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler

class PreprocessingEngine:
    def __init__(self):
        from sklearn.preprocessing import RobustScaler
        from sklearn.impute import SimpleImputer
        self.scaler = RobustScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.numeric_cols = []

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_processed = df.copy()
        if type(df_processed) != pd.DataFrame:
            return df_processed
        self.numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        
        if self.numeric_cols.empty:
            return df_processed

        df_processed[self.numeric_cols] = self.imputer.fit_transform(df_processed[self.numeric_cols])
        df_processed[self.numeric_cols] = self.scaler.fit_transform(df_processed[self.numeric_cols])
        return df_processed

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_processed = df.copy()
        if type(df_processed) != pd.DataFrame or len(self.numeric_cols) == 0:
            return df_processed
        
        # Only transform columns that actually exist in df
        cols_to_transform = [col for col in self.numeric_cols if col in df_processed.columns]
        if not cols_to_transform:
            return df_processed
            
        df_processed[cols_to_transform] = self.imputer.transform(df_processed[cols_to_transform])
        df_processed[cols_to_transform] = self.scaler.transform(df_processed[cols_to_transform])
        return df_processed

    @staticmethod
    def process(df: pd.DataFrame) -> pd.DataFrame:
        """
        Scales numerical columns robustly to handle outliers better.
        Stateless version for backwards compatibility.
        """
        engine = PreprocessingEngine()
        return engine.fit_transform(df)
