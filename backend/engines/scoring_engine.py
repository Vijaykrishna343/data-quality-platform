import math


class ScoringEngine:

    @staticmethod
    def calculate_score(missing_pct, duplicate_pct, outlier_pct, noisy_pct):
        """
        Advanced non-linear quality score calculation.
        """

        # Step 1: Strong weighted impact
        weighted_impact = (
            missing_pct * 2.0 +      # Missing hurts most
            duplicate_pct * 1.5 +    # Duplicates moderate
            outlier_pct * 1.3 +      # Outliers moderate
            noisy_pct * 1.7          # Noise strong penalty
        )

        # Step 2: Non-linear scaling (makes bad data drop faster)
        severity = math.log1p(weighted_impact) * 15

        score = 100 - severity

        score = max(min(score, 100), 0)

        return round(score, 2)

    @staticmethod
    def get_ml_readiness(score):
        """
        Classifies dataset ML readiness.
        """

        if score >= 90:
            return {
                "status": "ML Ready",
                "level": "high",
                "color": "green"
            }

        if score >= 75:
            return {
                "status": "Needs Minor Cleaning",
                "level": "medium",
                "color": "yellow"
            }

        if score >= 60:
            return {
                "status": "Needs Cleaning",
                "level": "low",
                "color": "orange"
            }

        return {
            "status": "Not ML Ready",
            "level": "critical",
            "color": "red"
        }

    @staticmethod
    def score_breakdown(missing_pct, duplicate_pct, outlier_pct, noisy_pct):
        """
        Returns detailed breakdown for frontend visualization.
        """

        return {
            "missing_impact": round(missing_pct * 2.0, 2),
            "duplicate_impact": round(duplicate_pct * 1.5, 2),
            "outlier_impact": round(outlier_pct * 1.3, 2),
            "noisy_impact": round(noisy_pct * 1.7, 2),
        }