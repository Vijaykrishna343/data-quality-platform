# ========================
# IMPORTS
# ========================
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

def _load_env_file_fallback():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


# ========================
# LOAD ENV VARIABLES
# ========================
if load_dotenv is not None:
    load_dotenv()
else:
    _load_env_file_fallback()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please check your .env file."
    )

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
