from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

# ✅ Database imports
from backend.database import engine
from backend.models import Base
from backend.config import CORS_ORIGINS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= GLOBAL EXCEPTION HANDLERS =================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "status_code": 422,
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
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