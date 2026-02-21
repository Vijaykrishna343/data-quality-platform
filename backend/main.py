from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analyze, clean, recommend

app = FastAPI(title="Data Quality Platform API")

# ---- CORS Middleware ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Include Routers ----
app.include_router(analyze.router)
app.include_router(clean.router)
app.include_router(recommend.router)


@app.get("/")
def root():
    return {"message": "Backend Running Successfully"}