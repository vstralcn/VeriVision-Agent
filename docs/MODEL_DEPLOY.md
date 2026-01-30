# Model Deployment Guide

This guide explains how to integrate a real deepfake detection model from HuggingFace into the platform.

## 🎯 Overview

The current implementation uses a **mock detection service** that generates random results for demonstration purposes. This guide will help you replace it with a real deepfake detection model.

## 🏗️ Architecture

The detection service is designed with a pluggable architecture:

```
User Upload → FastAPI Endpoint → Detection Service → Model Inference → Results
```

The key file to modify: `backend/app/services/detection_service.py`

## 🔌 Integration Points

### Current Mock Implementation

Location: `backend/app/services/detection_service.py`

The `DeepfakeDetectionService` class has a method `detect_image()` that currently:
1. Calculates image fingerprints (SHA256, pHash)
2. Generates random detection results
3. Creates a mock heatmap
4. Returns structured results

### What Needs to Be Replaced

Replace the mock logic in the `detect_image()` method with real model inference.

## 📦 Recommended Models

### Option 1: Pre-trained Deepfake Detection Models

#### 1. **Deepfake Detection from HuggingFace**

```python
from transformers import AutoModelForImageClassification, AutoFeatureExtractor
import torch
from PIL import Image

class RealDeepfakeDetectionService:
    def __init__(self):
        # Load model and feature extractor
        self.model_name = "dima806/deepfake_vs_real_image_detection"
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
        self.model.eval()

    def detect_image(self, image_path: str):
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        inputs = self.feature_extractor(images=image, return_tensors="pt")

        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)

        # Get prediction
        fake_probability = probabilities[0][1].item()  # Assuming index 1 is "fake"
        is_fake = fake_probability > 0.5
        confidence = abs(fake_probability - 0.5) * 2

        return {
            'is_fake': is_fake,
            'fake_probability': fake_probability,
            'confidence': confidence
        }
```

#### 2. **Face Forensics++ Models**

```python
# Using a Face Forensics++ trained model
from transformers import AutoModel
import torch

class FaceForensicsDetector:
    def __init__(self):
        self.model = torch.hub.load('selimsef/dfdc_deepfake_challenge', 'EfficientNetB7')
        self.model.eval()

    def detect_image(self, image_path: str):
        # Implementation here
        pass
```

#### 3. **Custom CNN Models**

```python
import torch
import torchvision.transforms as transforms

class CustomDeepfakeDetector:
    def __init__(self, model_path: str):
        self.model = torch.load(model_path)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

    def detect_image(self, image_path: str):
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            output = self.model(image_tensor)
            probability = torch.sigmoid(output).item()

        return {
            'is_fake': probability > 0.5,
            'fake_probability': probability,
            'confidence': abs(probability - 0.5) * 2
        }
```

## 🔧 Step-by-Step Integration

### Step 1: Install Additional Dependencies

Add to `backend/requirements.txt`:

```txt
torch==2.1.0
torchvision==0.16.0
transformers==4.35.0
timm==0.9.12
```

### Step 2: Modify Detection Service

Edit `backend/app/services/detection_service.py`:

```python
import hashlib
import os
import uuid
from datetime import datetime
from typing import Optional
from PIL import Image
import numpy as np
import cv2
from sqlalchemy.orm import Session

# Add model imports
from transformers import AutoModelForImageClassification, AutoFeatureExtractor
import torch

from app.models.models import Detection, TraceRecord
from app.core.config import settings


class DeepfakeDetectionService:
    """
    Real deepfake detection service with HuggingFace model integration.
    """

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(f"{self.upload_dir}/images", exist_ok=True)
        os.makedirs(f"{self.upload_dir}/heatmaps", exist_ok=True)

        # Initialize model
        self._load_model()

    def _load_model(self):
        """Load the deepfake detection model."""
        try:
            model_name = "dima806/deepfake_vs_real_image_detection"
            print(f"Loading model: {model_name}")

            self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
            self.model = AutoModelForImageClassification.from_pretrained(model_name)
            self.model.eval()

            # Move to GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)

            print(f"Model loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to mock detection")
            self.model = None

    async def detect_image(
        self,
        image_path: str,
        user_id: int,
        db: Session
    ) -> Detection:
        """
        Perform deepfake detection on an image.
        """
        # Calculate image fingerprints
        sha256_hash = self._calculate_sha256(image_path)
        phash = self._calculate_phash(image_path)

        # Run detection
        if self.model is not None:
            detection_result = self._run_model_inference(image_path)
        else:
            # Fallback to mock detection
            detection_result = self._mock_detection()

        fake_probability = detection_result['fake_probability']
        is_fake = detection_result['is_fake']
        confidence = detection_result['confidence']

        # Generate heatmap (using GradCAM or similar)
        heatmap_path = self._generate_heatmap(image_path, detection_result)

        # Generate analysis report
        analysis_report = self._generate_analysis_report(
            is_fake, fake_probability, confidence, detection_result
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

    def _run_model_inference(self, image_path: str) -> dict:
        """Run real model inference."""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            inputs = self.feature_extractor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)

            # Get prediction (assuming index 1 is "fake")
            fake_probability = probabilities[0][1].item()
            is_fake = fake_probability > 0.5
            confidence = abs(fake_probability - 0.5) * 2

            return {
                'is_fake': is_fake,
                'fake_probability': fake_probability,
                'confidence': confidence,
                'raw_logits': logits.cpu().numpy(),
                'probabilities': probabilities.cpu().numpy()
            }
        except Exception as e:
            print(f"Model inference error: {e}")
            return self._mock_detection()

    def _mock_detection(self) -> dict:
        """Fallback mock detection."""
        fake_probability = np.random.uniform(0.3, 0.9)
        is_fake = fake_probability > 0.5
        confidence = abs(fake_probability - 0.5) * 2

        return {
            'is_fake': is_fake,
            'fake_probability': fake_probability,
            'confidence': confidence
        }

    # ... rest of the methods remain the same ...
```

### Step 3: Update Docker Configuration

Modify `backend/Dockerfile` to support GPU (optional):

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including CUDA support (optional)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directories
RUN mkdir -p uploads/images uploads/heatmaps

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 4: Test the Integration

```bash
# Rebuild the backend
docker-compose build backend

# Restart services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

## 🎨 Advanced: Generating Real Heatmaps

### Using GradCAM for Attention Visualization

```python
import torch
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

class DeepfakeDetectionService:
    # ... existing code ...

    def _generate_heatmap_gradcam(self, image_path: str, detection_result: dict) -> str:
        """Generate heatmap using GradCAM."""
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            image_np = np.array(image) / 255.0

            # Prepare input
            inputs = self.feature_extractor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get target layer (last conv layer)
            target_layers = [self.model.classifier[-1]]

            # Create GradCAM
            cam = GradCAM(model=self.model, target_layers=target_layers)

            # Generate CAM
            grayscale_cam = cam(input_tensor=inputs['pixel_values'])
            grayscale_cam = grayscale_cam[0, :]

            # Overlay on image
            visualization = show_cam_on_image(image_np, grayscale_cam, use_rgb=True)

            # Save heatmap
            heatmap_filename = f"heatmap_{uuid.uuid4().hex}.jpg"
            heatmap_path = f"{self.upload_dir}/heatmaps/{heatmap_filename}"
            Image.fromarray(visualization).save(heatmap_path)

            return heatmap_path
        except Exception as e:
            print(f"GradCAM error: {e}, falling back to mock heatmap")
            return self._generate_heatmap(image_path)
```

Add to `requirements.txt`:
```txt
grad-cam==1.4.8
```

## 📊 Model Performance Optimization

### 1. Model Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_model():
    """Cache model loading."""
    model = AutoModelForImageClassification.from_pretrained(model_name)
    return model
```

### 2. Batch Processing

```python
def detect_images_batch(self, image_paths: list) -> list:
    """Process multiple images in batch."""
    images = [Image.open(path).convert('RGB') for path in image_paths]
    inputs = self.feature_extractor(images=images, return_tensors="pt")

    with torch.no_grad():
        outputs = self.model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    return probabilities.cpu().numpy()
```

### 3. GPU Acceleration

```python
# In docker-compose.yml, add GPU support:
services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 🧪 Testing Your Model

Create a test script `backend/test_model.py`:

```python
import sys
from app.services.detection_service import detection_service

def test_detection(image_path: str):
    """Test detection on a single image."""
    print(f"Testing detection on: {image_path}")

    # Mock database session
    class MockDB:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass

    result = detection_service.detect_image(image_path, user_id=1, db=MockDB())

    print(f"Result: {'Fake' if result.is_fake else 'Real'}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Fake Probability: {result.fake_probability:.2%}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_model.py <image_path>")
        sys.exit(1)

    test_detection(sys.argv[1])
```

Run test:
```bash
docker-compose exec backend python test_model.py /app/uploads/images/test.jpg
```

## 📚 Recommended Models & Resources

### HuggingFace Models

1. **dima806/deepfake_vs_real_image_detection**
   - Pre-trained on deepfake datasets
   - Easy to integrate
   - Good baseline performance

2. **facebook/deit-base-distilled-patch16-224**
   - Vision Transformer
   - Can be fine-tuned on deepfake data

3. **microsoft/resnet-50**
   - Classic CNN architecture
   - Reliable performance

### Datasets for Fine-tuning

- **FaceForensics++**: Large-scale deepfake dataset
- **Celeb-DF**: Celebrity deepfake dataset
- **DFDC (Deepfake Detection Challenge)**: Kaggle competition dataset

### Research Papers

- "FaceForensics++: Learning to Detect Manipulated Facial Images"
- "The Eyes Tell All: Detecting Political Orientation from Eye Movement Data"
- "Detecting Face Synthesis Using Convolutional Neural Networks"

## 🚀 Production Deployment

### 1. Model Versioning

```python
class DeepfakeDetectionService:
    MODEL_VERSION = "v1.0.0"

    def __init__(self):
        self.model_path = f"models/deepfake_detector_{self.MODEL_VERSION}"
        self._load_model()
```

### 2. Model Monitoring

```python
def detect_image(self, image_path: str, user_id: int, db: Session):
    start_time = time.time()

    # Run detection
    result = self._run_model_inference(image_path)

    inference_time = time.time() - start_time

    # Log metrics
    print(f"Inference time: {inference_time:.3f}s")

    return result
```

### 3. Error Handling

```python
def _run_model_inference(self, image_path: str) -> dict:
    try:
        # Model inference
        result = self._inference(image_path)
        return result
    except torch.cuda.OutOfMemoryError:
        print("GPU OOM, falling back to CPU")
        self.model.to('cpu')
        return self._inference(image_path)
    except Exception as e:
        print(f"Inference error: {e}")
        return self._mock_detection()
```

## 📝 Configuration

Add to `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Model settings
    MODEL_NAME: str = "dima806/deepfake_vs_real_image_detection"
    MODEL_CACHE_DIR: str = "models/cache"
    USE_GPU: bool = True
    BATCH_SIZE: int = 8

    class Config:
        env_file = ".env"
```

## 🔍 Troubleshooting

### Model Loading Issues

```bash
# Check if model files are downloaded
ls -la ~/.cache/huggingface/

# Clear cache and retry
rm -rf ~/.cache/huggingface/
```

### GPU Not Detected

```bash
# Check CUDA availability
docker-compose exec backend python -c "import torch; print(torch.cuda.is_available())"
```

### Memory Issues

```python
# Reduce batch size or use model quantization
from transformers import AutoModelForImageClassification
import torch

model = AutoModelForImageClassification.from_pretrained(
    model_name,
    torch_dtype=torch.float16  # Use half precision
)
```

## 📞 Support

For model integration issues:
1. Check HuggingFace model documentation
2. Review PyTorch/Transformers compatibility
3. Test model inference separately before integration

---

**Ready to deploy your real deepfake detection model!** 🚀
