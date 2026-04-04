import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")
UPLOAD_DIR = os.path.join(STORAGE_DIR, "uploads")
CLEANED_DIR = os.path.join(STORAGE_DIR, "cleaned")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CLEANED_DIR, exist_ok=True)

# ================= SECURITY SETTINGS =================
MAX_FILE_SIZE_MB = 100  # Max 100MB per file
ALLOWED_EXTENSIONS = {".csv"}

# ================= CORS SETTINGS =================
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]