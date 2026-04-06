from pydantic import BaseModel
from typing import List, Dict, Optional, Any


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


class UploadResponse(BaseModel):
    """Response for file upload endpoint"""
    dataset_id: int
    filename: str
    message: str


class ProfileResponse(BaseModel):
    """Response for dataset profile endpoint"""
    rows: int
    columns: int
    missing_percentage: float
    duplicate_percentage: float
    quality_score: float
    importance: Dict[str, float]


class PreviewResponse(BaseModel):
    """Response for dataset preview endpoint"""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int


class SimulationResponse(BaseModel):
    """Response for cleaning simulation"""
    score_before: float
    score_after: float
    improvement: float
    improvement_percent: float
    warning: Optional[str] = None
    rows_before: int
    rows_after: int
    rows_removed: int
    ml_readiness_after: Dict[str, str]


class ClassificationResponse(BaseModel):
    """Response for column type classification"""
    numeric: List[str]
    categorical: List[str]


class RecommendationResponse(BaseModel):
    """Response for cleaning recommendations"""
    recommendations: List[str]


class ErrorResponse(BaseModel):
    """Standard error response"""
    status_code: int
    detail: str
    error_type: str = "BadRequest"
