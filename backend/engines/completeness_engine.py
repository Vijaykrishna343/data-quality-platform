def calculate_completeness(df):
    total_cells = len(df) * len(df.columns)
    total_missing = df.isna().sum().sum()

    if total_cells == 0:
        return 0

    return (1 - total_missing / total_cells) * 100