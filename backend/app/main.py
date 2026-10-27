"""
AI-NIDS: FastAPI Application Entrypoint
Orchestrates API routers, database lifecycle, CORS configuration, and health telemetry.
"""

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.config import settings
from backend.app.database.session import init_db
from backend.app.services.seed_data import seed_initial_data_if_empty
from backend.app.services.traffic_monitor import monitor_service

from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.detect import router as detect_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.model import router as model_router
from backend.app.api.monitor import router as monitor_router

# Ensure database tables exist immediately upon module load
init_db()
seed_initial_data_if_empty()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    print("[*] AI-NIDS Backend running.")
    yield
    # Shutdown sequence
    print("[*] Shutting down AI-NIDS services...")
    monitor_service.stop_monitoring()
    print("[+] Cleanup complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Cybersecurity Network Intrusion Detection System with Machine Learning and Explainable AI.",
    lifespan=lifespan
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[!] Unhandled Exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing network telemetry."}
    )

# Root & Health check endpoints
@app.get("/health", tags=["System"])
def health_check():
    """System health check and operational state."""
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "database": "connected"
    }

@app.get("/", tags=["System"])
def root():
    return {
        "message": "AI-NIDS (Network Intrusion Detection System) API is active.",
        "documentation": "/docs",
        "version": settings.VERSION
    }

# Mount modular API routers under /api
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(detect_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)
app.include_router(model_router, prefix=settings.API_V1_PREFIX)
app.include_router(monitor_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
