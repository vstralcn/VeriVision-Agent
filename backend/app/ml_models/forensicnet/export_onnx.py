
from __future__ import annotations
import argparse
from pathlib import Path

import torch

from .model import ForensicNet

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True, help="runs/exp1/best.pt")
    ap.add_argument("--out", required=True, help="runs/exp1/model.onnx")
    ap.add_argument("--opset", type=int, default=17)
    args = ap.parse_args()

    device = torch.device("cpu")
    ckpt = torch.load(args.ckpt, map_location=device)
    model = ForensicNet(pretrained=False).to(device)
    model.load_state_dict(ckpt["model"], strict=True)
    model.eval()

    rgb = torch.randn(1, 3, 224, 224, device=device)
    freq = torch.randn(1, 2, 224, 224, device=device)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    torch.onnx.export(
        model,
        (rgb, freq),
        str(out_path),
        input_names=["rgb", "freq"],
        output_names=["cls_logit", "mask_logit"],
        dynamic_axes={
            "rgb": {0: "batch"},
            "freq": {0: "batch"},
            "cls_logit": {0: "batch"},
            "mask_logit": {0: "batch"},
        },
        opset_version=args.opset,
    )
    print("exported:", out_path)

if __name__ == "__main__":
    main()
