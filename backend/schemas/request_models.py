from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class SimulationRequest(BaseModel):
    """Validation schema for cleaning simulation"""
    handle_missing: bool = False
    remove_duplicates: bool = False
    outlier_method: Optional[str] = None  # "iqr" or "isolation_forest"
    drop_columns: List[str] = Field(default_factory=list)
    missing_method: str = Field(default="none", pattern="^(none|mean|median|mode|smart)$")
    outlier_action: str = Field(default="fix", pattern="^(fix|remove)$")
    noisy_method: str = Field(default="none")
    noisy_action: str = Field(default="fix", pattern="^(fix|remove)$")

    @field_validator("outlier_method")
    @classmethod
    def validate_outlier_method(cls, value: Optional[str]):
        if value and value not in ["iqr", "mad", "zscore", "isolation", "isolation_forest", "none"]:
            raise ValueError("Invalid outlier method")
        return value

    @field_validator("noisy_method")
    @classmethod
    def validate_noisy_method(cls, value: str):
        if value not in ["none", "zscore", "mad"]:
            raise ValueError("Invalid noisy method")
        return value


class DatasetFilterRequest(BaseModel):
    """Validation schema for dataset filtering"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=1000)
    
    
class AnalyticsRequest(BaseModel):
    """Validation schema for analytics queries"""
    dataset_id: int = Field(..., gt=0)
    include_correlations: bool = True
    sample_size: Optional[int] = Field(None, ge=100, le=50000)
