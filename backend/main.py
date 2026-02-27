from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.upload import router as upload_router
from backend.api.simulate import router as simulate_router
from backend.api.recommend import router as recommend_router
from backend.api.profile import router as profile_router
from backend.api.download import router as download_router
from backend.api.classification import router as classification_router

app = FastAPI(title="Intelligent Data Quality Platform")

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

app.include_router(upload_router)
app.include_router(profile_router)
app.include_router(classification_router)
app.include_router(recommend_router)
app.include_router(simulate_router)
app.include_router(download_router)

@app.get("/")
def root():
    return {"message": "Backend Running Successfully"}