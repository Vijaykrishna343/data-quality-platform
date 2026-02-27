class ScoringEngine:

    @staticmethod
    def calculate_score(missing_pct, duplicate_pct, outlier_pct):

        # Weighted formula
        score = (
            100
            - (missing_pct * 0.4)
            - (duplicate_pct * 0.3)
            - (outlier_pct * 0.3)
        )

        # Cap score
        if score > 99:
            score = 99

        if score < 0:
            score = 0

        return round(score, 2)