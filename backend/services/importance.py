def column_importance(df):
    scores = {}

    for col in df.columns:
        missing_ratio = df[col].isnull().mean()
        score = 100 - int(missing_ratio * 100)
        scores[col] = max(score, 0)

    return scores