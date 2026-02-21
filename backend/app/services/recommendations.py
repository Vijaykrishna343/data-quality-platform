def generate_recommendations(df):

    recommendations = []

    if df.isnull().sum().sum() > 0:
        recommendations.append("Handle missing values.")

    if df.duplicated().sum() > 0:
        recommendations.append("Remove duplicate rows.")

    if len(df.columns) > 20:
        recommendations.append("Consider reducing number of columns.")

    if not recommendations:
        recommendations.append("Dataset looks good.")

    return recommendations