
from __future__ import annotations
from typing import Dict, Any, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet50, ResNet50_Weights
from torchvision.models.feature_extraction import create_feature_extractor

class FreqEncoder(nn.Module):
    """A small CNN to encode frequency features (FFT + ELA)."""
    def __init__(self, in_ch: int = 2, out_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, 32, 3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.Conv2d(128, 256, 3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
        )
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.proj = nn.Linear(256, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.net(x)
        x = self.pool(x).flatten(1)
        x = self.proj(x)
        return x

class FPNDecoder(nn.Module):
    """
    Minimal FPN decoder for 1-channel mask.
    Takes ResNet features at strides 4,8,16,32: (c2,c3,c4,c5)
    """
    def __init__(self, c2=256, c3=512, c4=1024, c5=2048, fpn_dim: int = 256):
        super().__init__()
        self.l2 = nn.Conv2d(c2, fpn_dim, 1)
        self.l3 = nn.Conv2d(c3, fpn_dim, 1)
        self.l4 = nn.Conv2d(c4, fpn_dim, 1)
        self.l5 = nn.Conv2d(c5, fpn_dim, 1)

        self.smooth2 = nn.Conv2d(fpn_dim, fpn_dim, 3, padding=1)
        self.smooth3 = nn.Conv2d(fpn_dim, fpn_dim, 3, padding=1)
        self.smooth4 = nn.Conv2d(fpn_dim, fpn_dim, 3, padding=1)

        self.head = nn.Sequential(
            nn.Conv2d(fpn_dim, fpn_dim, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(fpn_dim, 1, 1)
        )

    def forward(self, c2, c3, c4, c5, out_size: Tuple[int,int]) -> torch.Tensor:
        p5 = self.l5(c5)
        p4 = self.l4(c4) + F.interpolate(p5, size=c4.shape[-2:], mode="bilinear", align_corners=False)
        p3 = self.l3(c3) + F.interpolate(p4, size=c3.shape[-2:], mode="bilinear", align_corners=False)
        p2 = self.l2(c2) + F.interpolate(p3, size=c2.shape[-2:], mode="bilinear", align_corners=False)

        p4 = self.smooth4(p4)
        p3 = self.smooth3(p3)
        p2 = self.smooth2(p2)

        # use p2 for high-res mask
        m = self.head(p2)
        m = F.interpolate(m, size=out_size, mode="bilinear", align_corners=False)
        return m

class ForensicNet(nn.Module):
    """
    Outputs:
    - cls_logit: (B,1)
    - mask_logit: (B,1,H,W)
    """
    def __init__(self, pretrained: bool = True, freq_dim: int = 256, dropout: float = 0.2):
        super().__init__()
        weights = ResNet50_Weights.DEFAULT if pretrained else None
        backbone = resnet50(weights=weights)

        return_nodes = {
            "layer1": "c2",
            "layer2": "c3",
            "layer3": "c4",
            "layer4": "c5",
        }
        self.backbone = create_feature_extractor(backbone, return_nodes=return_nodes)

        self.freq = FreqEncoder(in_ch=2, out_dim=freq_dim)

        self.cls_head = nn.Sequential(
            nn.Linear(2048 + freq_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(512, 1)
        )

        self.seg_head = FPNDecoder()

    def forward(self, rgb: torch.Tensor, freq: torch.Tensor) -> Dict[str, torch.Tensor]:
        feats = self.backbone(rgb)
        c2, c3, c4, c5 = feats["c2"], feats["c3"], feats["c4"], feats["c5"]

        # classification feature from c5 GAP
        rgb_vec = F.adaptive_avg_pool2d(c5, 1).flatten(1)
        freq_vec = self.freq(freq)
        x = torch.cat([rgb_vec, freq_vec], dim=1)
        cls_logit = self.cls_head(x)

        # segmentation mask
        H, W = rgb.shape[-2:]
        mask_logit = self.seg_head(c2, c3, c4, c5, out_size=(H, W))

        return {"cls_logit": cls_logit, "mask_logit": mask_logit}
