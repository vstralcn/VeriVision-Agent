import asyncio
import hashlib
import hmac
import logging
import os
import uuid
from datetime import datetime
from typing import Optional

import cv2
import numpy as np
import torch
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import settings
from app.ml_models.forensicnet.infer import load_model, predict
from app.models.models import Detection, TraceRecord
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when the configured detection model cannot be used."""


class InferenceError(RuntimeError):
    """Raised when model inference fails for an otherwise valid image."""


class DeepfakeDetectionService:
    """Run ForensicNet inference and persist attributable detection results."""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(f"{self.upload_dir}/images", exist_ok=True)
        os.makedirs(f"{self.upload_dir}/heatmaps", exist_ok=True)

        self.device = "cuda" if settings.USE_GPU and torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_error = "Model has not been initialized"

    def initialize(self) -> None:
        """Load the configured model without preventing the API from starting."""
        model_path = settings.MODEL_PATH
        if not os.path.isabs(model_path):
            model_path = os.path.abspath(model_path)
            if not os.path.exists(model_path):
                backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                model_path = os.path.join(backend_root, settings.MODEL_PATH)

        try:
            self.model = load_model(model_path, device=self.device)
            self.model_error = None
            logger.info("Detection model loaded from %s on %s", model_path, self.device)
        except Exception as e:
            self.model = None
            self.model_error = str(e)
            logger.error("Failed to load detection model from %s: %s", model_path, e)

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    async def detect_image(
        self,
        image_path: str,
        user_id: int,
        db: Session
    ) -> Detection:
        """
        Perform deepfake detection on an image using ForensicNet.
        """
        # Calculate image fingerprints
        sha256_hash = self._calculate_sha256(image_path)
        phash = self._calculate_phash(image_path)

        if self.model is None:
            raise ModelUnavailableError(self.model_error or "Detection model is unavailable")

        try:
            result = await asyncio.to_thread(self._predict_image, image_path)
            fake_probability = float(result.fake_prob)
            mask_prob = result.mask_prob
        except Exception as e:
            logger.exception("Prediction failed for %s", image_path)
            raise InferenceError("Detection model inference failed") from e

        is_fake = fake_probability > 0.5
        confidence = abs(fake_probability - 0.5) * 2

        # Generate heatmap
        heatmap_path = self._generate_heatmap(image_path, mask_prob)

        # Generate analysis report
        analysis_report = self._generate_analysis_report(is_fake, fake_probability, confidence)

        # Generate LLM explanation
        llm_explanation = await llm_service.generate_explanation(
            is_fake=is_fake,
            fake_probability=fake_probability,
            confidence=confidence,
            risk_level=analysis_report["risk_level"],
            analysis=analysis_report["analysis"],
            mask_prob=mask_prob,
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
            llm_explanation=llm_explanation,
            cert_id=cert_id,
            cert_signature=cert_signature,
            sha256=sha256_hash,
            phash=phash,
        )
        try:
            db.add(detection)
            db.flush()
            db.add_all([
                self._build_trace_record(
                    detection.id, "uploaded", "Image uploaded for detection"
                ),
                self._build_trace_record(
                    detection.id,
                    "detected",
                    f"Detection completed: {'Fake' if is_fake else 'Real'}",
                ),
            ])
            db.commit()
            db.refresh(detection)
        except Exception:
            db.rollback()
            if heatmap_path and os.path.exists(heatmap_path):
                os.remove(heatmap_path)
            raise

        return detection

    def _predict_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
        return predict(self.model, image_bytes, device=self.device, return_mask=True)

    def _calculate_sha256(self, image_path: str) -> str:
        """Calculate SHA256 hash of image file."""
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _calculate_phash(self, image_path: str) -> str:
        """Calculate a 64-bit DCT perceptual hash of the image."""
        with Image.open(image_path) as source_image:
            img = source_image.convert("L").resize(
                (32, 32), Image.Resampling.LANCZOS
            )
        dct = cv2.dct(np.asarray(img, dtype=np.float32))[:8, :8]
        median = np.median(dct.flatten()[1:])
        bits = (dct > median).flatten()
        return f"{int(''.join('1' if bit else '0' for bit in bits), 2):016x}"

    def _generate_heatmap(
        self, image_path: str, mask_prob: Optional[np.ndarray] = None
    ) -> Optional[str]:
        """
        Generate a heatmap visualization based on the model's mask prediction.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None

        height, width = img.shape[:2]

        if mask_prob is not None:
            # Resize mask to original image size
            mask_resized = cv2.resize(mask_prob, (width, height), interpolation=cv2.INTER_LINEAR)
            # Create heatmap from mask probability
            heatmap = (mask_resized * 255).astype(np.uint8)
        else:
            return None
            
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Blend with original image
        overlay = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

        # Save heatmap
        heatmap_filename = f"heatmap_{uuid.uuid4().hex}.jpg"
        heatmap_path = f"{self.upload_dir}/heatmaps/{heatmap_filename}"
        if cv2.imwrite(heatmap_path, overlay):
            return heatmap_path
        logger.error("Failed to write heatmap to %s", heatmap_path)
        return None

    def _generate_analysis_report(
        self, is_fake: bool, fake_probability: float, confidence: float
    ) -> dict:
        """Generate structured analysis report."""
        report = {
            "verdict": "Fake" if is_fake else "Real",
            "fake_probability": round(fake_probability, 4),
            "confidence": round(confidence, 4),
            "risk_level": self._get_risk_level(fake_probability),
            "analysis": {},
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
        data = f"{cert_id}:{sha256}".encode()
        key = settings.CERTIFICATION_KEY or settings.SECRET_KEY
        return hmac.new(key.encode(), data, hashlib.sha256).hexdigest()

    def verify_signature(self, cert_id: str, sha256: str, signature: str) -> bool:
        """Verify certification signature."""
        if not signature:
            return False
        expected_signature = self._generate_signature(cert_id, sha256)
        if hmac.compare_digest(signature, expected_signature):
            return True

        # Existing records used this legacy digest. New records use HMAC.
        legacy_data = f"{cert_id}:{sha256}:{settings.SECRET_KEY}"
        legacy_signature = hashlib.sha256(legacy_data.encode()).hexdigest()
        return hmac.compare_digest(signature, legacy_signature)

    def _build_trace_record(
        self, detection_id: int, action: str, description: str
    ) -> TraceRecord:
        return TraceRecord(
            detection_id=detection_id,
            action=action,
            description=description,
            meta_info={"timestamp": datetime.utcnow().isoformat()},
        )


# Singleton instance
detection_service = DeepfakeDetectionService()
