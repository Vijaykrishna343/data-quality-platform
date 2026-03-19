from pydantic import BaseModel
from typing import Optional


class SimulationRequest(BaseModel):
    handle_missing: bool = False
    remove_duplicates: bool = False
    outlier_method: Optional[str] = None  # "iqr" or "isolation_forest"