import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.models import AuditLog, Detection, TraceRecord, User
from app.schemas.schemas import (
    DetectionListResponse,
    DetectionResponse,
    TraceRecordResponse,
)
from app.services.detection_service import (
    InferenceError,
    ModelUnavailableError,
    detection_service,
)

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


def _get_authorized_detection(
    detection_id: int, db: Session, current_user: User
) -> Detection:
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )
    if detection.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this detection",
        )
    return detection


async def _save_validated_upload(file: UploadFile) -> str:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    image_dir = os.path.join(settings.UPLOAD_DIR, "images")
    os.makedirs(image_dir, exist_ok=True)
    upload_id = uuid.uuid4().hex
    staging_path = os.path.join(image_dir, f".{upload_id}.upload")
    total_size = 0

    try:
        with open(staging_path, "wb") as output:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Image exceeds the {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB limit",
                    )
                output.write(chunk)

        try:
            with Image.open(staging_path) as image:
                image_format = image.format
                width, height = image.size
                if width <= 0 or height <= 0 or width * height > settings.MAX_IMAGE_PIXELS:
                    raise ValueError("Image dimensions exceed the allowed limit")
                image.verify()
        except (
            Image.DecompressionBombError,
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is not a supported, decodable image",
            ) from exc

        extension = ALLOWED_IMAGE_FORMATS.get(image_format)
        if extension is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supported image formats are JPEG, PNG, and WebP",
            )

        final_path = os.path.join(image_dir, f"{upload_id}{extension}")
        os.replace(staging_path, final_path)
        return final_path
    finally:
        await file.close()
        if os.path.exists(staging_path):
            os.remove(staging_path)


def _record_failed_detection(db: Session, user_id: int, reason: str) -> None:
    try:
        db.rollback()
        db.add(AuditLog(
            user_id=user_id,
            action="detection",
            success=False,
            detail={"reason": reason},
        ))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist detection failure audit log")


def _serve_detection_file(path: str | None) -> FileResponse:
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection media is not available",
        )

    upload_root = os.path.realpath(settings.UPLOAD_DIR)
    resolved_path = os.path.realpath(path)
    if os.path.commonpath([upload_root, resolved_path]) != upload_root:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if not os.path.isfile(resolved_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(resolved_path)


@router.post("/upload", response_model=DetectionResponse)
async def upload_and_detect(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload an image and perform deepfake detection."""
    file_path = await _save_validated_upload(file)

    try:
        detection = await detection_service.detect_image(
            file_path, current_user.id, db
        )
    except ModelUnavailableError:
        if os.path.exists(file_path):
            os.remove(file_path)
        _record_failed_detection(db, current_user.id, "model_unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Detection model is unavailable",
        )
    except InferenceError:
        if os.path.exists(file_path):
            os.remove(file_path)
        _record_failed_detection(db, current_user.id, "inference_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detection model inference failed",
        )
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        _record_failed_detection(db, current_user.id, "internal_error")
        logger.exception("Detection request failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detection failed",
        )

    try:
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
    except Exception:
        db.rollback()
        logger.exception("Detection succeeded but its audit log could not be persisted")

    return detection


@router.get("/history", response_model=DetectionListResponse)
def get_detection_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's detection history."""
    query = db.query(Detection).filter(Detection.user_id == current_user.id)
    total = query.with_entities(func.count(Detection.id)).scalar() or 0
    fake_count = query.filter(Detection.is_fake.is_(True)).with_entities(
        func.count(Detection.id)
    ).scalar() or 0
    detections = (
        query
        .order_by(desc(Detection.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return DetectionListResponse(
        items=detections,
        total=total,
        fake_count=fake_count,
        real_count=total - fake_count,
    )


@router.get("/recent", response_model=list[DetectionResponse])
def get_recent_detections(
    limit: int = Query(5, ge=1, le=20),
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
    return _get_authorized_detection(detection_id, db, current_user)


@router.get("/{detection_id}/trace", response_model=list[TraceRecordResponse])
def get_trace_records(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trace records for a detection (traceability)."""
    _get_authorized_detection(detection_id, db, current_user)

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
    detection = _get_authorized_detection(detection_id, db, current_user)

    stored_hash_valid = (
        os.path.isfile(detection.image_path)
        and detection_service._calculate_sha256(detection.image_path) == detection.sha256
    )
    signature_valid = detection_service.verify_signature(
        detection.cert_id,
        detection.sha256,
        detection.cert_signature
    )
    is_valid = stored_hash_valid and signature_valid

    # Create trace record for verification
    trace_record = TraceRecord(
        detection_id=detection.id,
        action="verified",
        description=f"Certification {'verified' if is_valid else 'failed verification'}",
        meta_info={
            "verified_by": current_user.id,
            "result": is_valid,
            "stored_hash_valid": stored_hash_valid,
            "signature_valid": signature_valid,
        },
    )
    db.add(trace_record)
    db.commit()

    return {
        "cert_id": detection.cert_id,
        "is_valid": is_valid,
        "sha256": detection.sha256,
    }


@router.get("/{detection_id}/image")
def get_detection_image(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detection = _get_authorized_detection(detection_id, db, current_user)
    return _serve_detection_file(detection.image_path)


@router.get("/{detection_id}/heatmap")
def get_detection_heatmap(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detection = _get_authorized_detection(detection_id, db, current_user)
    return _serve_detection_file(detection.heatmap_path)
