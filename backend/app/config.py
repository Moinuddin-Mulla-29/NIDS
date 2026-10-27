"""
AI-NIDS: Application Configuration
Centralized configuration management with environment variable overrides.
"""

import os
from typing import List

class Settings:
    PROJECT_NAME: str = "AI-NIDS: Intelligent Intrusion Detection System"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api"

    # Environment
    ENV: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # CORS Whitelist (Permits Vite React dev server)
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Database
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "backend", "data")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(DATA_DIR, 'nids.db')}"
    )

    # Machine Learning Artifacts
    ML_DIR: str = os.path.join(BASE_DIR, "ml")
    SAVED_MODELS_DIR: str = os.path.join(ML_DIR, "saved_models")
    PREPROCESSOR_PATH: str = os.path.join(SAVED_MODELS_DIR, "preprocessor.joblib")
    BEST_MODEL_PATH: str = os.path.join(SAVED_MODELS_DIR, "best_model.joblib")
    METRICS_PATH: str = os.path.join(SAVED_MODELS_DIR, "metrics.json")

    # Upload Constraints (Defense against DOS & resource exhaustion)
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: set = {".csv"}

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
