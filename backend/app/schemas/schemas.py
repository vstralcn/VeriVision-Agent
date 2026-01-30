from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Detection schemas
class DetectionCreate(BaseModel):
    pass


class DetectionResponse(BaseModel):
    id: int
    user_id: int
    image_path: str
    heatmap_path: Optional[str]
    is_fake: bool
    confidence: float
    fake_probability: float
    analysis_report: Optional[Dict[str, Any]]
    cert_id: str
    cert_signature: Optional[str]
    sha256: Optional[str]
    phash: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Trace Record schemas
class TraceRecordResponse(BaseModel):
    id: int
    detection_id: int
    action: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Audit Log schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource: Optional[str]
    success: bool
    ip_address: Optional[str]
    user_agent: Optional[str]
    detail: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Admin schemas
class DashboardStats(BaseModel):
    today_detection_count: int
    today_fake_count: int
    today_fake_ratio: float
    total_users: int
    total_detections: int


class UserManagementResponse(UserResponse):
    detection_count: int
