import pandas as pd
from backend.engines.outlier_engine import OutlierEngine
from backend.engines.scoring_engine import ScoringEngine


class CleaningEngine:

    @staticmethod
    def apply_cleaning(df: pd.DataFrame, strategy: str):

        if strategy == "drop_missing":
            df = df.dropna()

        elif strategy == "remove_duplicates":
            df = df.drop_duplicates()

        elif strategy == "remove_both":
            df = df.dropna().drop_duplicates()

        elif strategy == "fill_mean":
            numeric_cols = df.select_dtypes(include="number").columns
            for col in numeric_cols:
                df[col].fillna(df[col].mean(), inplace=True)

        elif strategy == "fill_mode":
            for col in df.columns:
                df[col].fillna(df[col].mode()[0], inplace=True)

        return df

    @staticmethod
    def simulate_cleaning(df: pd.DataFrame, strategy: str, outlier_method: str = "iqr"):

        df_copy = df.copy()

        rows_before = len(df)
        missing_ratio_before = df.isnull().mean().mean()
        duplicate_ratio_before = df.duplicated().mean()

        if outlier_method == "iqr":
            _, outlier_percent_before = OutlierEngine.detect_iqr(df)
        else:
            _, outlier_percent_before = OutlierEngine.detect_isolation_forest(df)

        score_before = ScoringEngine.calculate_quality_score(
            missing_ratio_before,
            duplicate_ratio_before,
            outlier_percent_before / 100
        )

        df_copy = CleaningEngine.apply_cleaning(df_copy, strategy)

        rows_after = len(df_copy)
        missing_ratio_after = df_copy.isnull().mean().mean()
        duplicate_ratio_after = df_copy.duplicated().mean()

        if outlier_method == "iqr":
            _, outlier_percent_after = OutlierEngine.detect_iqr(df_copy)
        else:
            _, outlier_percent_after = OutlierEngine.detect_isolation_forest(df_copy)

        score_after = ScoringEngine.calculate_quality_score(
            missing_ratio_after,
            duplicate_ratio_after,
            outlier_percent_after / 100
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