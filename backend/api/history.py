from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Dataset, AnalysisResult

# ✅ IMPORTANT: router must exist
router = APIRouter(prefix="/history", tags=["History"])


@router.get("/")
def get_history(db: Session = Depends(get_db)):

    datasets = db.query(Dataset).all()

    history = []

    for dataset in datasets:
        # Get latest analysis result
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.dataset_id == dataset.id)
            .order_by(AnalysisResult.id.desc())
            .first()
        )

        history.append({
            "dataset_id": dataset.id,
            "name": dataset.name,
            "created_at": dataset.created_at,
            "analysis": analysis.result if analysis else None
        })

    return history