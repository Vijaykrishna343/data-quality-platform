
from backend.database import SessionLocal
from backend.models import Dataset

db = SessionLocal()
datasets = db.query(Dataset).all()
for ds in datasets:
    print(f"ID: {ds.id}, Name: {ds.name}, Path: {ds.file_path}")
db.close()
