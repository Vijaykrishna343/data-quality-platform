# ========================
# IMPORTS
# ========================
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

# ========================
# LOAD ENV VARIABLES
# ========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ========================
# DATABASE ENGINE
# ========================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # avoids stale connections
)

# ========================
# SESSION CONFIG
# ========================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ========================
# BASE CLASS FOR MODELS
# ========================
Base = declarative_base()

# ========================
# DB DEPENDENCY (FASTAPI)
# ========================
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()