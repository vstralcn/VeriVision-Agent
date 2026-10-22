from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.core.database import get_db
from app.models.models import AuditLog, Detection, LLMConfig, User
from app.schemas.schemas import (
    AuditLogListResponse,
    AuditLogResponse,
    DashboardStats,
    LLMConfigResponse,
    LLMConfigUpdate,
    LLMTestResult,
    UserManagementListResponse,
    UserManagementResponse,
    UserResponse,
)
from app.services.llm_service import llm_service

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get admin dashboard statistics."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # Today's detection count
    today_detection_count = (
        db.query(func.count(Detection.id))
        .filter(
            and_(
                Detection.created_at >= today_start,
                Detection.created_at <= today_end
            )
        )
        .scalar()
    )

    # Today's fake count
    today_fake_count = (
        db.query(func.count(Detection.id))
        .filter(
            and_(
                Detection.created_at >= today_start,
                Detection.created_at <= today_end,
                Detection.is_fake.is_(True)
            )
        )
        .scalar()
    )

    # Calculate fake ratio
    today_fake_ratio = (
        today_fake_count / today_detection_count
        if today_detection_count > 0
        else 0.0
    )

    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Total detections
    total_detections = db.query(func.count(Detection.id)).scalar()

    return DashboardStats(
        today_detection_count=today_detection_count or 0,
        today_fake_count=today_fake_count or 0,
        today_fake_ratio=round(today_fake_ratio, 4),
        total_users=total_users or 0,
        total_detections=total_detections or 0,
    )


@router.get("/users", response_model=UserManagementListResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get all users for management."""
    total = db.query(func.count(User.id)).scalar() or 0
    rows = (
        db.query(User, func.count(Detection.id).label("detection_count"))
        .outerjoin(Detection, Detection.user_id == User.id)
        .group_by(User.id)
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for user, detection_count in rows:
        result.append(
            UserManagementResponse(
                id=user.id,
                email=user.email,
                nickname=user.nickname,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                detection_count=detection_count or 0,
            )
        )

    return UserManagementListResponse(items=result, total=total)


@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Enable or disable a user account."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from disabling themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account",
        )

    # Toggle active status
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    # Log admin action
    audit_log = AuditLog(
        user_id=current_admin.id,
        action="admin_action",
        resource=f"user:{user_id}",
        success=True,
        detail={
            "action": "toggle_active",
            "target_user": user_id,
            "new_status": user.is_active,
        },
    )
    db.add(audit_log)
    db.commit()

    return user


@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    success: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get audit logs with filtering."""
    query = db.query(AuditLog)

    # Apply filters
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if success is not None:
        query = query.filter(AuditLog.success == success)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    total = query.with_entities(func.count(AuditLog.id)).scalar() or 0
    audit_logs = (
        query.order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return AuditLogListResponse(items=audit_logs, total=total)


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse)
def get_audit_log_detail(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get detailed audit log entry."""
    audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()

    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return audit_log


# ──────────────────────────────────────────
# LLM / AI Agent configuration
# ──────────────────────────────────────────

def _get_or_create_llm_config(db: Session) -> LLMConfig:
    config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
    if not config:
        config = LLMConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def _to_response(config: LLMConfig) -> LLMConfigResponse:
    return LLMConfigResponse(
        id=config.id,
        provider=config.provider or "openai",
        api_base_url=config.api_base_url or "https://api.openai.com/v1",
        api_key_masked=llm_service.mask_key(config.api_key or ""),
        model=config.model or "gpt-4o-mini",
        enabled=bool(config.enabled),
        max_tokens=config.max_tokens or 512,
        temperature=config.temperature if config.temperature is not None else 0.3,
        updated_at=config.updated_at,
    )


@router.get("/llm-config", response_model=LLMConfigResponse)
def get_llm_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Get the current LLM / AI agent configuration (API key is masked)."""
    config = _get_or_create_llm_config(db)
    return _to_response(config)


@router.put("/llm-config", response_model=LLMConfigResponse)
def update_llm_config(
    data: LLMConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Update the LLM / AI agent configuration and reload the service."""
    config = _get_or_create_llm_config(db)

    if data.provider is not None:
        config.provider = data.provider
    if data.api_base_url is not None:
        config.api_base_url = data.api_base_url
    if data.api_key is not None and data.api_key != "":
        config.api_key = data.api_key
    if data.model is not None:
        config.model = data.model
    if data.enabled is not None:
        config.enabled = data.enabled
    if data.max_tokens is not None:
        config.max_tokens = data.max_tokens
    if data.temperature is not None:
        config.temperature = data.temperature

    db.commit()
    db.refresh(config)

    # Hot-reload the singleton so the next detection uses the new settings
    llm_service.reload_config(config)

    # Audit log
    audit = AuditLog(
        user_id=current_admin.id,
        action="admin_action",
        resource="llm_config",
        success=True,
        detail={"action": "update_llm_config", "model": config.model, "enabled": config.enabled},
    )
    db.add(audit)
    db.commit()

    return _to_response(config)


@router.post("/llm-config/test", response_model=LLMTestResult)
async def test_llm_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Test the current LLM configuration by sending a minimal request."""
    result = await llm_service.test_connection()
    return LLMTestResult(**result)
