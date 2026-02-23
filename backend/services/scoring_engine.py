def compute_quality_score(metrics: dict) -> float:
    """
    Computes overall quality score as weighted average of metrics.
    Score is between 0 and 100.
    """

    if not metrics:
        return 0.0

    weights = {
        "completeness": 0.4,
        "uniqueness": 0.3,
        "validity": 0.3
    }

    total_score = 0.0
    total_weight = 0.0

    for metric_name, weight in weights.items():
        value = metrics.get(metric_name, 0)

        # Ensure value is between 0 and 100
        if value is None:
            value = 0

        value = max(0, min(100, float(value)))

        total_score += value * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(total_score / total_weight, 2)