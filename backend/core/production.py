import time
import psutil
import logging
import asyncio
from fastapi import Request, APIRouter, Depends
from fastapi.responses import JSONResponse
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.database import get_db

logger = logging.getLogger("production_logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Basic Request Throttling Strategy
class RateLimiter:
    def __init__(self, requests_per_minute=300):
        self.requests_per_minute = requests_per_minute
        self.ips = defaultdict(list)

    def check(self, ip):
        current_time = time.time()
        self.ips[ip] = [t for t in self.ips[ip] if current_time - t < 60]
        if len(self.ips[ip]) >= self.requests_per_minute:
            return False
        self.ips[ip].append(current_time)
        return True

limiter = RateLimiter(requests_per_minute=300)

async def production_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    
    # 1. IP Rate Limiting
    if not limiter.check(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    start_time = time.time()
    
    # 2. Timeout Protection
    try:
        response = await asyncio.wait_for(call_next(request), timeout=180)
    except asyncio.TimeoutError:
        logger.error(f"Timeout Error: Request {request.method} {request.url.path}")
        return JSONResponse(status_code=504, content={"detail": "Request Timeout"})
    except Exception as e:
        logger.error(f"Runtime Error {request.url.path}: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 3. Structured Performance Logging
    logger.info(f"[API_REQUEST] method={request.method} path={request.url.path} latency_sec={round(process_time, 4)} status_code={response.status_code} ip={client_ip}")
    
    return response

# 4. Production Health Check endpoints
health_router = APIRouter(tags=["Production Diagnostics"])

@health_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    metrics = {
        "status": "healthy",
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_mb": round(psutil.virtual_memory().available / (1024*1024), 2)
        },
        "database": "disconnected"
    }
    
    # Check DB Connection
    try:
        db.execute(text("SELECT 1"))
        metrics["database"] = "connected"
    except Exception as e:
         metrics["status"] = "degraded"
         metrics["database"] = str(e)
         logger.error(f"Database health check failed: {str(e)}")
         
    return metrics
