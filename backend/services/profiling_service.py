import pandas as pd

def profile_dataset(file_path):

    df = pd.read_csv(file_path)

    column_profiles = []

    for col in df.columns:
        col_data = df[col]

        missing = col_data.isna().sum()
        duplicates = col_data.duplicated().sum()
        outliers = 0

        if pd.api.types.is_numeric_dtype(col_data):
            series = col_data.dropna()
            if len(series) > 5:
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = len(series[(series < lower) | (series > upper)])

        column_profiles.append({
            "name": col,
            "type": str(col_data.dtype),
            "missing_count": int(missing),
            "duplicate_count": int(duplicates),
            "outlier_count": int(outliers)
        })

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_profiles": column_profiles,
        "total_missing": int(df.isna().sum().sum()),
        "total_duplicates": int(df.duplicated().sum())
    }