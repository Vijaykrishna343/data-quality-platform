import pandas as pd
from engines.completeness_engine import calculate_completeness
from engines.uniqueness_engine import calculate_uniqueness
from engines.consistency_engine import calculate_consistency
from engines.outlier_engine import calculate_outlier_stability


def calculate_quality(file_path: str):

    df = pd.read_csv(file_path)

    completeness = calculate_completeness(df)
    uniqueness = calculate_uniqueness(df)
    consistency = calculate_consistency(df)
    outlier_stability = calculate_outlier_stability(df)

    score = (
        0.4 * completeness +
        0.2 * uniqueness +
        0.2 * consistency +
        0.2 * outlier_stability
    )

    return {
        "value": round(score, 2),
        "metrics": {
            "completeness": round(completeness, 2),
            "uniqueness": round(uniqueness, 2),
            "consistency": round(consistency, 2),
            "outlier_stability": round(outlier_stability, 2)
        }
    }