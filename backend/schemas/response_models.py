from pydantic import BaseModel
from typing import List, Dict


class ScoreResponse(BaseModel):
    value: float
    metrics: Dict


class AnalyzeResponse(BaseModel):
    score_before: Dict
    score_after: Dict
    column_importance: List[Dict]
    drop_recommendations: List[Dict]
    correlation_matrix: Dict
    cleaned_preview: List[Dict]