class SummaryEngine:

    @staticmethod
    def generate(profile, analysis=None, simulation=None):

        insights = []

        # ---------------- PROFILE SUMMARY ----------------
        insights.append(
            f"The dataset contains {profile['rows']} rows and "
            f"{profile['columns']} columns."
        )

        insights.append(
            f"Initial data quality score is {profile['quality_score']}%."
        )

        # ---------------- ANALYSIS INSIGHTS ----------------
        if analysis:

            if analysis.get("missing_percentage", 0) > 5:
                insights.append(
                    "Significant missing values detected. "
                    "Handling them will improve model stability."
                )

            if analysis.get("duplicate_count", 0) > 0:
                insights.append(
                    "Duplicate rows detected. "
                    "Removing duplicates will reduce bias."
                )

            if analysis.get("outlier_percentage", 0) > 5:
                insights.append(
                    "High outlier presence detected. "
                    "Outlier treatment recommended."
                )

        # ---------------- SIMULATION IMPACT ----------------
        if simulation:
            improvement = simulation["score_after"] - simulation["score_before"]

            insights.append(
                f"After cleaning, the quality score improved by "
                f"{round(improvement, 2)}%."
            )

            if improvement > 5:
                insights.append(
                    "Cleaning had a significant positive impact."
                )
            elif improvement > 0:
                insights.append(
                    "Cleaning slightly improved dataset health."
                )
            else:
                insights.append(
                    "Cleaning had minimal measurable impact."
                )

        # ---------------- ML READINESS ----------------
        if simulation:
            final_score = simulation["score_after"]
        else:
            final_score = profile["quality_score"]

        if final_score > 85:
            insights.append(
                "Dataset is ML-ready and suitable for training models."
            )
        elif final_score > 70:
            insights.append(
                "Dataset is moderately ready. Minor preprocessing advised."
            )
        else:
            insights.append(
                "Dataset requires further cleaning before ML usage."
            )

        return insights