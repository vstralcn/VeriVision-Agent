import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.models import User, Detection, TraceRecord, AuditLog
from app.schemas.schemas import DetectionResponse, TraceRecordResponse
from app.services.detection_service import detection_service
from app.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=DetectionResponse)
async def upload_and_detect(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload an image and perform deepfake detection."""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = f"{settings.UPLOAD_DIR}/images/{filename}"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Perform detection
    try:
        detection = await detection_service.detect_image(
            file_path, current_user.id, db
        )

        # Log detection action
        audit_log = AuditLog(
            user_id=current_user.id,
            action="detection",
            resource=f"detection:{detection.id}",
            success=True,
            detail={
                "detection_id": detection.id,
                "is_fake": detection.is_fake,
                "confidence": detection.confidence,
            },
        )
        db.add(audit_log)
        db.commit()

        return detection
    except Exception as e:
        # Log failed detection
        audit_log = AuditLog(
            user_id=current_user.id,
            action="detection",
            success=False,
            detail={"error": str(e)},
        )
        db.add(audit_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection failed: {str(e)}",
        )


@router.get("/history", response_model=List[DetectionResponse])
def get_detection_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's detection history."""
    detections = (
        db.query(Detection)
        .filter(Detection.user_id == current_user.id)
        .order_by(desc(Detection.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return detections


@router.get("/recent", response_model=List[DetectionResponse])
def get_recent_detections(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent detections for dashboard."""
    detections = (
        db.query(Detection)
        .filter(Detection.user_id == current_user.id)
        .order_by(desc(Detection.created_at))
        .limit(limit)
        .all()
    )
    return detections


@router.get("/{detection_id}", response_model=DetectionResponse)
def get_detection(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific detection details."""
    detection = db.query(Detection).filter(Detection.id == detection_id).first()

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    # Check ownership
    if detection.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this detection",
        )

    return detection


@router.get("/{detection_id}/trace", response_model=List[TraceRecordResponse])
def get_trace_records(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trace records for a detection (traceability)."""
    detection = db.query(Detection).filter(Detection.id == detection_id).first()

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    # Check ownership
    if detection.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this detection",
        )

    trace_records = (
        db.query(TraceRecord)
        .filter(TraceRecord.detection_id == detection_id)
        .order_by(TraceRecord.created_at)
        .all()
    )

    return trace_records


@router.post("/{detection_id}/verify")
def verify_certification(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify the trusted certification signature."""
    detection = db.query(Detection).filter(Detection.id == detection_id).first()

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    # Verify signature
    is_valid = detection_service.verify_signature(
        detection.cert_id,
        detection.sha256,
        detection.cert_signature
    )

    # Create trace record for verification
    trace_record = TraceRecord(
        detection_id=detection.id,
        action="verified",
        description=f"Certification {'verified' if is_valid else 'failed verification'}",
        metadata={"verified_by": current_user.id, "result": is_valid},
    )
    db.add(trace_record)
    db.commit()

    return {
        "cert_id": detection.cert_id,
        "is_valid": is_valid,
        "sha256": detection.sha256,
    }


@router.get("/image/{filename}")
def get_image(filename: str):
    """Serve uploaded image."""
    file_path = f"{settings.UPLOAD_DIR}/images/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    return FileResponse(file_path)


@router.get("/heatmap/{filename}")
def get_heatmap(filename: str):
    """Serve heatmap image."""
    file_path = f"{settings.UPLOAD_DIR}/heatmaps/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heatmap not found",
        )
    return FileResponse(file_path)
