from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 Relationship (one dataset → many analysis results)
    analysis_results = relationship("AnalysisResult", back_populates="dataset")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    result = Column(JSONB)

    # 🔥 Reverse relationship
    dataset = relationship("Dataset", back_populates="analysis_results")