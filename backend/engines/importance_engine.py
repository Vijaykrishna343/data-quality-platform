import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import LabelEncoder

class ImportanceEngine:

    @staticmethod
    def calculate(df: pd.DataFrame):
        if df.empty:
            return {}

        # 1. Prepare Data for ML
        df_ml = df.copy()
        
        # Identify numeric vs categorical vs datetime
        numeric_cols = df_ml.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df_ml.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df_ml.select_dtypes(include=['datetime']).columns.tolist()
        
        # Simple Label Encoding for categoricals
        le = LabelEncoder()
        for col in categorical_cols:
            df_ml[col] = le.fit_transform(df_ml[col].astype(str))

        # Convert datetimes to numeric (timestamps)
        for col in datetime_cols:
            df_ml[col] = pd.to_numeric(df_ml[col], errors='coerce')
            
        # Fill NaNs for ML
        numeric_means = df_ml.mean(numeric_only=True)
        df_ml = df_ml.fillna(numeric_means if not numeric_means.empty else 0)

        # 2. Select a Proxy Target
        if df_ml.shape[1] < 2:
            return {col: 100 for col in df.columns}

        # Select target: column with highest variance that isn't an ID
        variances = df_ml.var(numeric_only=True)
        if variances.empty:
              target_col = df_ml.columns[-1]
        else:
              target_col = variances.idxmax()

        X = df_ml.drop(columns=[target_col])
        y = df_ml[target_col]

        if X.empty:
             return {target_col: 100}

        try:
            # Drop any remaining non-numeric columns just in case
            X_numeric = X.select_dtypes(include=[np.number])
            if X_numeric.empty:
                 return {col: 50.0 for col in df.columns}
                 
            # 3. Random Forest Importance (Tree-based)
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X_numeric, y)
            rf_importances = rf.feature_importances_

            # 4. Mutual Information (Statistical)
            mi_scores = mutual_info_regression(X_numeric, y, random_state=42)

            # 5. Hybrid Scoring
            def normalize(arr):
                bottom = arr.min()
                top = arr.max()
                if top == bottom: return np.ones_like(arr) * 0.5
                return (arr - bottom) / (top - bottom)

            rf_norm = normalize(rf_importances)
            mi_norm = normalize(mi_scores)

            hybrid_scores = (rf_norm * 0.6) + (mi_norm * 0.4)
            
            importance_map = {}
            for i, col in enumerate(X_numeric.columns):
                importance_map[col] = round(float(hybrid_scores[i] * 100), 2)
            
            importance_map[target_col] = 100.0

            # For columns not in X_numeric (if any were dropped)
            for col in df.columns:
                if col not in importance_map:
                    importance_map[col] = 0.0

        except Exception:
            importance_map = {col: 50.0 for col in df.columns}

        sorted_scores = dict(
            sorted(
                importance_map.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

        return sorted_scores