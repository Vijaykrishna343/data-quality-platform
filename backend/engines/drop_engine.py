def recommend_drop(df, importance_scores):

    recommendations = []

    for col in df.columns:

        importance = importance_scores.get(col, {}).get("importance", 100)

        missing_percentage = df[col].isna().mean() * 100

        if importance < 50 or missing_percentage > 40:
            recommendations.append(col)

    return recommendations