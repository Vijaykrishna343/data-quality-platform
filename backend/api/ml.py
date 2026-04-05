import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from backend.database import get_db
from backend.models import Dataset
from backend.core.file_manager import read_csv
from backend.engines.ml_engine import MLEngine

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

class MLTrainRequest(BaseModel):
    target_column: str
    task_type: str = "classification"

@router.post("/train/{dataset_id}")
def train_model(dataset_id: int, payload: MLTrainRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    file_path = dataset.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    df = read_csv(file_path)
    if payload.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{payload.target_column}' not found.")
        
    try:
        model, metrics = MLEngine.train_model(df, target_col=payload.target_column, task_type=payload.task_type)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plot/{plot_type}")
def get_plot(plot_type: str):
    filename = "shap_summary.png" if plot_type == "summary" else "shap_feature_importance_bar.png"
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Plot not found")
    return FileResponse(filename)
