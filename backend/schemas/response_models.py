from pydantic import BaseModel
from typing import List

class AnalyzeResponse(BaseModel):
    rows: int
    columns: int
    quality_score: int
    reasons: List[str]