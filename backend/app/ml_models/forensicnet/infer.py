
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import io

import numpy as np
import cv2
import torch

from .model import ForensicNet
from .utils import compute_ela_rgb, compute_fft_mag, rgb_to_gray01
from .data import IMAGENET_MEAN, IMAGENET_STD

@dataclass
class InferenceResult:
    fake_prob: float
    mask_prob: Optional[np.ndarray]  # HxW float32 in [0,1] if requested

def _preprocess(image_bytes: bytes, img_size: int = 224) -> Tuple[torch.Tensor, torch.Tensor]:
    # decode
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("Invalid image bytes")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # resize to square (simple)
    img_rgb = cv2.resize(img_rgb, (img_size, img_size), interpolation=cv2.INTER_AREA)

    # rgb tensor
    x = img_rgb.astype(np.float32) / 255.0
    x = (x - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    rgb_t = torch.from_numpy(x).permute(2,0,1).unsqueeze(0)

    # freq tensor
    gray01 = rgb_to_gray01(img_rgb)
    fft = compute_fft_mag(gray01)
    ela = compute_ela_rgb(img_rgb, quality=95)
    ela_gray = rgb_to_gray01((ela * 255).astype(np.uint8))
    ela_gray = (ela_gray - ela_gray.mean()) / (ela_gray.std() + 1e-6)
    freq = np.stack([fft, ela_gray], axis=0).astype(np.float32)
    freq_t = torch.from_numpy(freq).unsqueeze(0)

    return rgb_t, freq_t

@torch.no_grad()
def load_model(ckpt_path: str, device: str = "cpu") -> ForensicNet:
    dev = torch.device(device)
    ckpt = torch.load(ckpt_path, map_location=dev)
    model = ForensicNet(pretrained=False).to(dev)
    model.load_state_dict(ckpt["model"], strict=True)
    model.eval()
    return model

@torch.no_grad()
def predict(model: ForensicNet, image_bytes: bytes, device: str = "cpu", return_mask: bool = True) -> InferenceResult:
    dev = torch.device(device)
    rgb_t, freq_t = _preprocess(image_bytes, img_size=224)
    rgb_t = rgb_t.to(dev)
    freq_t = freq_t.to(dev)

    out = model(rgb_t, freq_t)
    fake_prob = torch.sigmoid(out["cls_logit"]).item()

    mask_prob = None
    if return_mask:
        mask_prob = torch.sigmoid(out["mask_logit"]).squeeze().cpu().numpy().astype(np.float32)

    return InferenceResult(fake_prob=fake_prob, mask_prob=mask_prob)
