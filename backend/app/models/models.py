from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # user or admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    detections = relationship("Detection", back_populates="user")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String, nullable=False)
    heatmap_path = Column(String, nullable=True)

    # Detection results
    is_fake = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    fake_probability = Column(Float, nullable=False)

    # Analysis report
    analysis_report = Column(JSON, nullable=True)

    # Trusted certification
    cert_id = Column(String, unique=True, nullable=False)
    cert_signature = Column(String, nullable=True)

    # Image fingerprints
    sha256 = Column(String, nullable=True)
    phash = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="detections")
    trace_records = relationship("TraceRecord", back_populates="detection")


class TraceRecord(Base):
    __tablename__ = "trace_records"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=False)

    action = Column(String, nullable=False)  # uploaded, detected, verified
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    detection = relationship("Detection", back_populates="trace_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # login, detection, admin_action
    resource = Column(String, nullable=True)  # e.g., "detection:123"
    success = Column(Boolean, default=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    detail = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
