"""Configuration module using Pydantic Settings - FIXED for Storage"""

import os
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # FastAPI
    app_name: str = "AI Video Editor"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/video_editor"
    )
    
    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production-min-32-chars!!!"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # ✅ FIX: S3 / Object Storage - Using UPPERCASE for consistency
    S3_ENDPOINT_URL: str = os.getenv(
        "S3_ENDPOINT_URL",
        "http://minio:9000"  # Local dev default (MinIO)
    )
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "ai-video-editor")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_USE_SSL: bool = os.getenv("S3_USE_SSL", "false").lower() == "true"
    
    # ✅ FIX: Temp directory with cross-platform support
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/ai_video_editor")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "524288000"))  # 500MB
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:8000"
        ).split(",")
    ]
    
    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    
    # Ollama (Optional LLM)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
    
    # Video Processing
    VIDEO_PRESET: str = os.getenv("VIDEO_PRESET", "medium")
    MAX_VIDEO_DURATION: int = int(os.getenv("MAX_VIDEO_DURATION", "600"))
    
    def __init__(self, **data):
        super().__init__(**data)
        # Use Redis URLs for Celery
        self.CELERY_BROKER_URL = self.REDIS_URL
        self.CELERY_RESULT_BACKEND = self.REDIS_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
