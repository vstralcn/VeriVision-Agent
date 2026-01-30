import hashlib
import os
import uuid
from datetime import datetime
from typing import Optional
from PIL import Image
import numpy as np
import cv2
from sqlalchemy.orm import Session
from app.models.models import Detection, TraceRecord
from app.core.config import settings


class DeepfakeDetectionService:
    """
    Mock deepfake detection service.
    In production, this would integrate with a real ML model from HuggingFace.
    """

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(f"{self.upload_dir}/images", exist_ok=True)
        os.makedirs(f"{self.upload_dir}/heatmaps", exist_ok=True)

    async def detect_image(
        self,
        image_path: str,
        user_id: int,
        db: Session
    ) -> Detection:
        """
        Perform deepfake detection on an image.
        This is a MOCK implementation - replace with real model inference.
        """
        # Calculate image fingerprints
        sha256_hash = self._calculate_sha256(image_path)
        phash = self._calculate_phash(image_path)

        # Mock detection results (in production, call real model here)
        fake_probability = np.random.uniform(0.3, 0.9)
        is_fake = fake_probability > 0.5
        confidence = abs(fake_probability - 0.5) * 2

        # Generate heatmap
        heatmap_path = self._generate_heatmap(image_path)

        # Generate analysis report
        analysis_report = self._generate_analysis_report(
            is_fake, fake_probability, confidence
        )

        # Generate trusted certification
        cert_id = self._generate_cert_id()
        cert_signature = self._generate_signature(cert_id, sha256_hash)

        # Create detection record
        detection = Detection(
            user_id=user_id,
            image_path=image_path,
            heatmap_path=heatmap_path,
            is_fake=is_fake,
            confidence=confidence,
            fake_probability=fake_probability,
            analysis_report=analysis_report,
            cert_id=cert_id,
            cert_signature=cert_signature,
            sha256=sha256_hash,
            phash=phash,
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)

        # Create trace records
        self._create_trace_record(
            db, detection.id, "uploaded", "Image uploaded for detection"
        )
        self._create_trace_record(
            db,
            detection.id,
            "detected",
            f"Detection completed: {'Fake' if is_fake else 'Real'}"
        )

        return detection

    def _calculate_sha256(self, image_path: str) -> str:
        """Calculate SHA256 hash of image file."""
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _calculate_phash(self, image_path: str) -> str:
        """Calculate perceptual hash of image."""
        img = Image.open(image_path).convert('L')
        img = img.resize((8, 8), Image.Resampling.LANCZOS)
        pixels = np.array(img).flatten()
        avg = pixels.mean()
        phash = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
        return hex(int(phash, 2))[2:].zfill(16)

    def _generate_heatmap(self, image_path: str) -> str:
        """
        Generate a mock heatmap visualization.
        In production, this would show model attention/manipulation areas.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None

        # Create mock heatmap (random hot spots)
        height, width = img.shape[:2]
        heatmap = np.random.rand(height, width) * 255
        heatmap = heatmap.astype(np.uint8)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Blend with original image
        overlay = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)

        # Save heatmap
        heatmap_filename = f"heatmap_{uuid.uuid4().hex}.jpg"
        heatmap_path = f"{self.upload_dir}/heatmaps/{heatmap_filename}"
        cv2.imwrite(heatmap_path, overlay)

        return heatmap_path

    def _generate_analysis_report(
        self, is_fake: bool, fake_probability: float, confidence: float
    ) -> dict:
        """Generate structured analysis report."""
        report = {
            "verdict": "Fake" if is_fake else "Real",
            "fake_probability": round(fake_probability, 4),
            "confidence": round(confidence, 4),
            "risk_level": self._get_risk_level(fake_probability),
            "analysis": {
                "face_manipulation": round(np.random.uniform(0.1, 0.9), 4),
                "texture_inconsistency": round(np.random.uniform(0.1, 0.9), 4),
                "lighting_artifacts": round(np.random.uniform(0.1, 0.9), 4),
                "compression_anomalies": round(np.random.uniform(0.1, 0.9), 4),
            },
            "summary": self._generate_summary(is_fake, fake_probability),
            "recommendations": self._generate_recommendations(is_fake),
        }
        return report

    def _get_risk_level(self, fake_probability: float) -> str:
        """Determine risk level based on fake probability."""
        if fake_probability < 0.3:
            return "Low"
        elif fake_probability < 0.6:
            return "Medium"
        else:
            return "High"

    def _generate_summary(self, is_fake: bool, fake_probability: float) -> str:
        """Generate human-readable summary."""
        if is_fake:
            return (
                f"This image shows signs of manipulation with {fake_probability*100:.1f}% "
                "probability. Multiple indicators suggest artificial generation or editing."
            )
        else:
            return (
                f"This image appears authentic with {(1-fake_probability)*100:.1f}% "
                "confidence. No significant manipulation indicators detected."
            )

    def _generate_recommendations(self, is_fake: bool) -> list:
        """Generate recommendations based on detection result."""
        if is_fake:
            return [
                "Verify the source of this image",
                "Cross-reference with original sources if available",
                "Consider additional forensic analysis",
                "Do not use for official purposes without verification",
            ]
        else:
            return [
                "Image appears authentic but always verify source",
                "Check metadata for additional information",
                "Consider context when evaluating authenticity",
            ]

    def _generate_cert_id(self) -> str:
        """Generate unique certification ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = uuid.uuid4().hex[:8].upper()
        return f"CERT-{timestamp}-{random_part}"

    def _generate_signature(self, cert_id: str, sha256: str) -> str:
        """Generate cryptographic signature for certification."""
        data = f"{cert_id}:{sha256}:{settings.SECRET_KEY}"
        signature = hashlib.sha256(data.encode()).hexdigest()
        return signature

    def verify_signature(self, cert_id: str, sha256: str, signature: str) -> bool:
        """Verify certification signature."""
        expected_signature = self._generate_signature(cert_id, sha256)
        return signature == expected_signature

    def _create_trace_record(
        self, db: Session, detection_id: int, action: str, description: str
    ):
        """Create a trace record for audit trail."""
        trace_record = TraceRecord(
            detection_id=detection_id,
            action=action,
            description=description,
            metadata={"timestamp": datetime.utcnow().isoformat()},
        )
        db.add(trace_record)
        db.commit()


# Singleton instance
detection_service = DeepfakeDetectionService()
