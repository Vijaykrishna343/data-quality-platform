def generate_recommendations(profile):
    recommendations = []

    if profile["missing_total"] > 0:
        recommendations.append("Consider handling missing values.")

    if profile["duplicates"] > 0:
        recommendations.append("Remove duplicate rows.")

    if not recommendations:
        recommendations.append("Dataset looks clean and reliable.")

    return recommendations