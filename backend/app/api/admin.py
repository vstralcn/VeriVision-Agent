from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.models.models import User, Detection, AuditLog
from app.schemas.schemas import (
    DashboardStats,
    UserManagementResponse,
    AuditLogResponse,
    UserResponse,
)

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
                Detection.is_fake == True
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


@router.get("/users", response_model=List[UserManagementResponse])
def get_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get all users for management."""
    users = db.query(User).offset(skip).limit(limit).all()

    result = []
    for user in users:
        detection_count = (
            db.query(func.count(Detection.id))
            .filter(Detection.user_id == user.id)
            .scalar()
        )
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

    return result


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


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
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

    # Order by most recent first
    audit_logs = (
        query.order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return audit_logs


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
