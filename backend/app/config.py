"""Configuration module using Pydantic Settings"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # FastAPI
    app_name: str = "AI Video Editor"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/video_editor"
    )
    
    # Redis
    redis_url: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    
    # Security
    secret_key: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production-min-32-chars!!!"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # S3 / Object Storage
    s3_endpoint: str = os.getenv(
        "S3_ENDPOINT",
        "http://minio:9000"  # Local dev default (MinIO)
    )
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    s3_bucket: str = os.getenv("S3_BUCKET", "video-editor")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_secure: bool = os.getenv("S3_SECURE", "false").lower() == "true"
    
    # CORS
    cors_origins: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:8000"
        ).split(",")
    ]
    
    # Celery
    celery_broker_url: str = None
    celery_result_backend: str = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Use Redis URLs for Celery
        self.celery_broker_url = self.redis_url
        self.celery_result_backend = self.redis_url
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
