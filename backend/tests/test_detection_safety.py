import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import Headers

from app.api.detection import _get_authorized_detection, _save_validated_upload
from app.core.config import settings
from app.core.database import Base
from app.models.models import Detection, User
from app.services.detection_service import (
    DeepfakeDetectionService,
    ModelUnavailableError,
)


def _image_bytes(image_format: str = "PNG") -> bytes:
    output = BytesIO()
    Image.new("RGB", (16, 16), color=(20, 40, 60)).save(output, format=image_format)
    return output.getvalue()


def _upload(data: bytes, content_type: str = "image/png") -> UploadFile:
    return UploadFile(
        filename="upload.bin",
        file=BytesIO(data),
        headers=Headers({"content-type": content_type}),
    )


def test_upload_uses_decoded_format_and_rejects_oversize(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 1024)

    saved_path = asyncio.run(_save_validated_upload(_upload(_image_bytes())))
    assert saved_path.endswith(".png")
    assert Image.open(saved_path).format == "PNG"

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(_save_validated_upload(_upload(b"x" * 1025)))
    assert exc_info.value.status_code == 413
    assert not list((tmp_path / "images").glob("*.upload"))


def test_model_unavailable_never_creates_a_detection(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    image_path = tmp_path / "input.png"
    image_path.write_bytes(_image_bytes())

    service = DeepfakeDetectionService()
    service.model = None
    service.model_error = "missing checkpoint"

    class FailOnDatabaseAccess:
        def __getattr__(self, name):
            raise AssertionError(f"database should not be accessed: {name}")

    with pytest.raises(ModelUnavailableError):
        asyncio.run(service.detect_image(str(image_path), 1, FailOnDatabaseAccess()))


def test_detection_access_is_limited_to_owner_or_admin():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    owner = User(email="owner@example.com", hashed_password="hash", role="user")
    other = User(email="other@example.com", hashed_password="hash", role="user")
    admin = User(email="admin@example.com", hashed_password="hash", role="admin")
    session.add_all([owner, other, admin])
    session.flush()
    detection = Detection(
        user_id=owner.id,
        image_path="uploads/images/example.png",
        is_fake=False,
        confidence=0.8,
        fake_probability=0.1,
        cert_id="CERT-1",
    )
    session.add(detection)
    session.commit()

    assert _get_authorized_detection(detection.id, session, owner).id == detection.id
    assert _get_authorized_detection(detection.id, session, admin).id == detection.id
    with pytest.raises(HTTPException) as exc_info:
        _get_authorized_detection(detection.id, session, other)
    assert exc_info.value.status_code == 403


def test_hmac_signature_rejects_modified_hash(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "CERTIFICATION_KEY", "test-certification-key")
    service = DeepfakeDetectionService()

    signature = service._generate_signature("CERT-1", "abc123")
    assert service.verify_signature("CERT-1", "abc123", signature)
    assert not service.verify_signature("CERT-1", "modified", signature)
