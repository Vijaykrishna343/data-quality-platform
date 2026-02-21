def calculate_quality_score(profile: dict):
    score = 100
    reasons = []

    if profile["missing_total"] > 0:
        penalty = min(30, profile["missing_total"])
        score -= penalty
        reasons.append("Dataset contains missing values.")

    if profile["duplicates"] > 0:
        penalty = min(20, profile["duplicates"] * 2)
        score -= penalty
        reasons.append("Duplicate rows detected.")

    score = max(0, score)

    return score, reasons