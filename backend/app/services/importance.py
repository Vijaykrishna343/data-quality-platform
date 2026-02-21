def column_importance(df):

    scores = {}

    for col in df.columns:
        missing_ratio = df[col].isnull().mean()
        uniqueness_ratio = df[col].nunique() / len(df)

        score = (1 - missing_ratio) * 50 + uniqueness_ratio * 50
        scores[col] = round(score, 2)

    return scores