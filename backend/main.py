from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analyze

app = FastAPI(title="Data Quality Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)