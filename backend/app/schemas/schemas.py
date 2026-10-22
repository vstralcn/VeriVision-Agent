from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    nickname: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    is_active: bool
    created_at: datetime

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


# Detection schemas
class DetectionCreate(BaseModel):
    pass


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_path: str
    heatmap_path: Optional[str]
    is_fake: bool
    confidence: float
    fake_probability: float
    analysis_report: Optional[Dict[str, Any]]
    llm_explanation: Optional[Dict[str, Any]]
    cert_id: str
    cert_signature: Optional[str]
    sha256: Optional[str]
    phash: Optional[str]
    created_at: datetime

class DetectionListResponse(BaseModel):
    items: List[DetectionResponse]
    total: int
    fake_count: int
    real_count: int


# Trace Record schemas
class TraceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    detection_id: int
    action: str
    description: Optional[str]
    meta_info: Optional[Dict[str, Any]]
    created_at: datetime

# Audit Log schemas
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    action: str
    resource: Optional[str]
    success: bool
    ip_address: Optional[str]
    user_agent: Optional[str]
    detail: Optional[Dict[str, Any]]
    created_at: datetime

class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int


# Admin schemas
class DashboardStats(BaseModel):
    today_detection_count: int
    today_fake_count: int
    today_fake_ratio: float
    total_users: int
    total_detections: int


class UserManagementResponse(UserResponse):
    detection_count: int


class UserManagementListResponse(BaseModel):
    items: List[UserManagementResponse]
    total: int


# LLM Config schemas
class LLMConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    api_base_url: str
    api_key_masked: str
    model: str
    enabled: bool
    max_tokens: int
    temperature: float
    updated_at: Optional[datetime] = None

class LLMConfigUpdate(BaseModel):
    provider: Optional[Literal["openai", "anthropic"]] = None
    api_base_url: Optional[str] = Field(default=None, max_length=2048)
    api_key: Optional[str] = Field(default=None, max_length=4096)
    model: Optional[str] = Field(default=None, min_length=1, max_length=200)
    enabled: Optional[bool] = None
    max_tokens: Optional[int] = Field(default=None, ge=64, le=4096)
    temperature: Optional[float] = Field(default=None, ge=0, le=2)


class LLMTestResult(BaseModel):
    success: bool
    message: str
    response_preview: Optional[str] = None
