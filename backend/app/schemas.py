"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Auth Schemas
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Project Schemas
class ProjectCreate(BaseModel):
    """Create project request"""
    title: str = Field(..., min_length=1, max_length=200)
    prompt: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update project request"""
    title: Optional[str] = None
    prompt: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response"""
    id: str
    user_id: str
    title: str
    prompt: Optional[str]
    status: str
    output_video_key: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Asset Schemas
class AssetType(str, Enum):
    """Asset type enum"""
    VIDEO = "video"
    IMAGE = "image"


class PresignedURLRequest(BaseModel):
    """Request for presigned URL"""
    asset_type: AssetType
    filename: str


class PresignedURLResponse(BaseModel):
    """Presigned URL response"""
    presigned_url: str
    s3_key: str
    upload_expires_in: int = 3600


class AssetMetadata(BaseModel):
    """Asset metadata"""
    s3_key: str
    filename: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None


class AssetCreate(BaseModel):
    """Create asset after upload"""
    s3_key: str
    filename: str
    asset_type: AssetType
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None


class AssetResponse(BaseModel):
    """Asset response"""
    id: str
    project_id: str
    asset_type: str
    s3_key: str
    filename: str
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    file_size_bytes: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Schemas
class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    """Job response"""
    id: str
    project_id: str
    celery_task_id: Optional[str]
    status: str
    progress_percent: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StartEditRequest(BaseModel):
    """Request to start editing a project"""
    project_id: str


class StartEditResponse(BaseModel):
    """Response when starting edit"""
    job_id: str
    celery_task_id: Optional[str]
    status: str
