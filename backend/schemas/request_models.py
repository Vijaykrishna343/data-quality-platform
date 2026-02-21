from pydantic import BaseModel

class CleanRequest(BaseModel):
    remove_duplicates: bool = True
    missing_strategy: str = "median"