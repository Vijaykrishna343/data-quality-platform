from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Database imports
from backend.database import engine
from backend.models import Base

# ================= APP INITIALIZATION =================

app = FastAPI(
    title="Intelligent Data Quality API",
    description="Professional Data Profiling, Cleaning & Analytics Platform",
    version="2.0.0"
)

# ================= DATABASE INIT =================

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# ================= ROUTER IMPORTS =================

from backend.api.upload import router as upload_router
from backend.api.profile import router as profile_router
from backend.api.classification import router as classification_router
from backend.api.simulate import router as simulate_router
from backend.api.recommend import router as recommend_router
from backend.api.download import router as download_router
from backend.api.analytics import router as analytics_router  
from backend.api.history import router as history_router

# ================= CORS CONFIGURATION =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROUTERS =================

app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(profile_router, prefix="/profile", tags=["Profile"])
app.include_router(classification_router, prefix="/classify", tags=["Classification"])
app.include_router(simulate_router, prefix="/simulate", tags=["Simulation"])
app.include_router(recommend_router, prefix="/recommend", tags=["Recommendation"])
app.include_router(download_router, prefix="/download", tags=["Download"])
app.include_router(history_router)

# Analytics already has prefix inside file
app.include_router(analytics_router)

# ================= HEALTH CHECK =================

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Backend Running Successfully",
        "version": "2.0.0"
    }