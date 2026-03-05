
from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
import albumentations as A

from .utils import compute_ela_rgb, compute_fft_mag, rgb_to_gray01

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD  = (0.229, 0.224, 0.225)

@dataclass
class Sample:
    img_path: str
    label: int
    mask_path: Optional[str] = None

def read_csv(csv_path: str) -> List[Sample]:
    samples: List[Sample] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_path = row["img_path"]
            label = int(row["label"])
            mask_path = row.get("mask_path", "") or None
            samples.append(Sample(img_path=img_path, label=label, mask_path=mask_path))
    return samples

def default_train_aug(img_size: int = 224) -> A.Compose:
    return A.Compose([
        A.LongestMaxSize(max_size=img_size),
        A.PadIfNeeded(min_height=img_size, min_width=img_size, border_mode=cv2.BORDER_REFLECT_101),
        A.RandomCrop(height=img_size, width=img_size),
        A.HorizontalFlip(p=0.5),
        A.OneOf([
            A.MotionBlur(blur_limit=5, p=0.5),
            A.GaussianBlur(blur_limit=(3, 5), p=0.5),
        ], p=0.2),
        A.ColorJitter(p=0.3),
        A.ImageCompression(quality_lower=60, quality_upper=100, p=0.3),
    ])

def default_val_aug(img_size: int = 224) -> A.Compose:
    return A.Compose([
        A.LongestMaxSize(max_size=img_size),
        A.PadIfNeeded(min_height=img_size, min_width=img_size, border_mode=cv2.BORDER_REFLECT_101),
        A.CenterCrop(height=img_size, width=img_size),
    ])

def to_tensor_img(img_rgb: np.ndarray) -> torch.Tensor:
    # img_rgb uint8 HWC -> float CHW
    x = img_rgb.astype(np.float32) / 255.0
    x = (x - np.array(IMAGENET_MEAN, dtype=np.float32)) / np.array(IMAGENET_STD, dtype=np.float32)
    x = torch.from_numpy(x).permute(2, 0, 1).contiguous()
    return x

class ForensicDataset(Dataset):
    """
    输出：
    - rgb: FloatTensor [3,H,W]
    - freq: FloatTensor [2,H,W] (FFT_mag, ELA_gray)
    - y: FloatTensor [1]
    - mask: FloatTensor [1,H,W] (0/1)
    - mask_valid: BoolTensor [1]  (是否对该样本计算 seg loss)
    """
    def __init__(self, csv_path: str, train: bool = True, img_size: int = 224):
        self.samples = read_csv(csv_path)
        self.train = train
        self.img_size = img_size
        self.aug = default_train_aug(img_size) if train else default_val_aug(img_size)

    def __len__(self) -> int:
        return len(self.samples)

    def _read_image_rgb(self, path: str) -> np.ndarray:
        img_bgr = cv2.imread(path, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise FileNotFoundError(f"Cannot read image: {path}")
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return img_rgb

    def _read_mask01(self, path: str) -> np.ndarray:
        m = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if m is None:
            raise FileNotFoundError(f"Cannot read mask: {path}")
        # binarize
        m = (m > 0).astype(np.uint8) * 255
        return m

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        s = self.samples[idx]
        img_rgb = self._read_image_rgb(s.img_path)

        mask = None
        has_mask = False
        if s.mask_path is not None and Path(s.mask_path).exists():
            mask = self._read_mask01(s.mask_path)
            has_mask = True

        # Albumentations expects HWC, mask HW
        if mask is None:
            augmented = self.aug(image=img_rgb)
            img_rgb = augmented["image"]
        else:
            augmented = self.aug(image=img_rgb, mask=mask)
            img_rgb = augmented["image"]
            mask = augmented["mask"]

        H, W = img_rgb.shape[:2]
        # build mask tensor
        if mask is None:
            mask01 = np.zeros((H, W), dtype=np.float32)
        else:
            mask01 = (mask.astype(np.float32) / 255.0)
            mask01 = (mask01 > 0.5).astype(np.float32)

        # seg supervision rule:
        # - real images: supervise zeros (valid)
        # - fake images: supervise only when mask exists; otherwise skip
        if s.label == 0:
            mask_valid = True
        else:
            mask_valid = bool(has_mask)

        rgb_t = to_tensor_img(img_rgb)

        # Frequency features computed from augmented image
        gray01 = rgb_to_gray01(img_rgb)  # 0..1 float
        fft = compute_fft_mag(gray01)  # standardized
        ela = compute_ela_rgb(img_rgb, quality=95)
        ela_gray = rgb_to_gray01((ela * 255).astype(np.uint8))  # 0..1

        # standardize ELA gray per-image
        ela_gray = (ela_gray - ela_gray.mean()) / (ela_gray.std() + 1e-6)

        freq = np.stack([fft, ela_gray], axis=0).astype(np.float32)  # [2,H,W]
        freq_t = torch.from_numpy(freq)

        y = torch.tensor([float(s.label)], dtype=torch.float32)
        mask_t = torch.from_numpy(mask01).unsqueeze(0)  # [1,H,W]
        mask_valid_t = torch.tensor([1 if mask_valid else 0], dtype=torch.bool)

        return {
            "rgb": rgb_t,
            "freq": freq_t,
            "y": y,
            "mask": mask_t,
            "mask_valid": mask_valid_t
        }
