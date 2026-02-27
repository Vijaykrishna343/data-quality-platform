class ScoringEngine:

    @staticmethod
    def calculate_score(missing_pct, duplicate_pct, outlier_pct):
        """
        Calculates weighted quality score.
        """

        weights = {
            "missing": 0.4,
            "duplicate": 0.3,
            "outlier": 0.3,
        }

        score = (
            100
            - (missing_pct * weights["missing"])
            - (duplicate_pct * weights["duplicate"])
            - (outlier_pct * weights["outlier"])
        )

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
    def score_breakdown(missing_pct, duplicate_pct, outlier_pct):
        """
        Returns detailed breakdown for frontend visualization.
        """

        return {
            "missing_impact": round(missing_pct * 0.4, 2),
            "duplicate_impact": round(duplicate_pct * 0.3, 2),
            "outlier_impact": round(outlier_pct * 0.3, 2),
        }