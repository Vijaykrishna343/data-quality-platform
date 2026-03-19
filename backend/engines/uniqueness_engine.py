def calculate_uniqueness(df):
    total_rows = len(df)
    duplicate_rows = df.duplicated().sum()

    if total_rows == 0:
        return 0

    return (1 - duplicate_rows / total_rows) * 100