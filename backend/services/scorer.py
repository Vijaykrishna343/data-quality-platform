def calculate_quality_score(profile: dict):
    """
    Calculates weighted normalized quality score.

    Weights:
    - Completeness → 40%
    - Duplicate Score → 30%
    - Outlier Score → 30%
    """

    rows = profile["rows"]
    columns = profile["columns"]

    total_cells = rows * columns if rows * columns > 0 else 1

    # ---- Completeness Score ----
    completeness_ratio = profile["completeness_ratio"]
    completeness_score = completeness_ratio * 100

    # ---- Duplicate Score ----
    duplicate_ratio = profile["duplicate_rows"] / rows if rows > 0 else 0
    duplicate_score = (1 - duplicate_ratio) * 100

    # ---- Outlier Score ----
    outlier_ratio = profile["outlier_count"] / rows if rows > 0 else 0
    outlier_score = (1 - outlier_ratio) * 100

    # ---- Weighted Final Score ----
    final_score = (
        0.4 * completeness_score +
        0.3 * duplicate_score +
        0.3 * outlier_score
    )

    final_score = round(max(0, min(final_score, 100)), 2)

    # ---- Generate Reasons ----
    reasons = []

    if profile["missing_values"] > 0:
        reasons.append("Dataset contains missing values.")

    if profile["duplicate_rows"] > 0:
        reasons.append("Duplicate rows detected.")

    if profile["outlier_count"] > 0:
        reasons.append("Outliers detected in numeric columns.")

    if not reasons:
        reasons.append("Dataset is clean and reliable.")

    return final_score, reasons