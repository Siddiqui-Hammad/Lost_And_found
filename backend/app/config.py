import os
from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    PROJECT_NAME: str = "TRACE AI - Smart AI + IoT Lost & Found System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "trace-ai-super-secret-jwt-key-2026-campus")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # MongoDB Config
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "trace_ai_db")
    
    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    
    # AI Matching Engine Weights (Configurable 0.0 - 1.0)
    WEIGHT_TEXT: float = 0.40       # 40% Text semantic embedding similarity
    WEIGHT_CATEGORY: float = 0.20   # 20% Category exact/fuzzy match
    WEIGHT_LOCATION: float = 0.15   # 15% Campus spatial proximity
    WEIGHT_COLOR: float = 0.10      # 10% Color match
    WEIGHT_TIME: float = 0.10       # 10% Temporal window match
    WEIGHT_BRAND: float = 0.05      # 5% Brand/make match
    
    # Classification Thresholds
    THRESHOLD_HIGH: float = 90.0
    THRESHOLD_POSSIBLE: float = 70.0
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
