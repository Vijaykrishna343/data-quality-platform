from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analyze, clean, recommend

app = FastAPI(title="Data Quality API")

# Enable CORS (important for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(clean.router)
app.include_router(recommend.router)

@app.get("/")
def root():
    return {"message": "Data Quality API running successfully"}