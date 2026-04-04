import pandas as pd

from backend.core.file_manager import read_csv
from backend.engines.completeness_engine import CompletenessEngine
from backend.engines.uniqueness_engine import calculate_uniqueness
from backend.engines.consistency_engine import calculate_consistency
from backend.engines.outlier_engine import OutlierEngine


def calculate_quality(file_path: str):

    df = read_csv(file_path)

    completeness = CompletenessEngine.calculate(df)
    uniqueness = calculate_uniqueness(df)
    consistency = calculate_consistency(df)
    outlier_percentage = OutlierEngine.detect_percentage(df, "iqr")

    score = (
        0.4 * completeness +
        0.2 * uniqueness +
        0.2 * consistency +
        0.2 * (100 - outlier_percentage)
    )

    return {
        "value": round(score, 2),
        "metrics": {
            "completeness": round(completeness, 2),
            "uniqueness": round(uniqueness, 2),
            "consistency": round(consistency, 2),
            "outlier_stability": round(100 - outlier_percentage, 2)
        }
    }