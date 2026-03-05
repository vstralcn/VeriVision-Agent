
from __future__ import annotations
import argparse
import os
from pathlib import Path
from typing import Dict

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, accuracy_score
from tqdm import tqdm

from .data import ForensicDataset
from .model import ForensicNet

def dice_loss(logits: torch.Tensor, targets: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    probs = torch.sigmoid(logits)
    num = 2 * (probs * targets).sum(dim=(1,2,3))
    den = (probs + targets).sum(dim=(1,2,3)) + eps
    dice = 1 - (num / den)
    return dice.mean()

@torch.no_grad()
def evaluate(model: ForensicNet, loader: DataLoader, device: torch.device) -> Dict[str, float]:
    model.eval()
    ys, ps = [], []
    for batch in loader:
        rgb = batch["rgb"].to(device)
        freq = batch["freq"].to(device)
        y = batch["y"].to(device)
        out = model(rgb, freq)
        p = torch.sigmoid(out["cls_logit"])
        ys.append(y.cpu().numpy().reshape(-1))
        ps.append(p.cpu().numpy().reshape(-1))
    y_all = np.concatenate(ys)
    p_all = np.concatenate(ps)
    auc = roc_auc_score(y_all, p_all) if len(np.unique(y_all)) > 1 else float("nan")
    acc = accuracy_score(y_all, (acc := (p_all >= 0.5).astype(np.int32)))
    return {"auc": float(auc), "acc": float(acc)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train_csv", required=True)
    ap.add_argument("--val_csv", required=True)
    ap.add_argument("--out_dir", default="runs/exp")
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--weight_decay", type=float, default=0.05)
    ap.add_argument("--seg_weight", type=float, default=0.5)
    ap.add_argument("--num_workers", type=int, default=4)
    ap.add_argument("--fp16", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_ds = ForensicDataset(args.train_csv, train=True, img_size=224)
    val_ds = ForensicDataset(args.val_csv, train=False, img_size=224)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.num_workers, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.num_workers, pin_memory=True)

    model = ForensicNet(pretrained=True).to(device)

    # pos_weight for BCE if imbalance; estimate from train set quickly
    labels = np.array([s.label for s in train_ds.samples], dtype=np.int32)
    n_pos = max(1, int(labels.sum()))
    n_neg = max(1, int((labels==0).sum()))
    pos_weight = torch.tensor([n_neg / n_pos], dtype=torch.float32, device=device)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)

    scaler = torch.cuda.amp.GradScaler(enabled=args.fp16 and device.type == "cuda")

    best_auc = -1.0
    bce = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    for epoch in range(1, args.epochs + 1):
        model.train()
        pbar = tqdm(train_loader, desc=f"epoch {epoch}/{args.epochs}")
        loss_meter = []

        for batch in pbar:
            rgb = batch["rgb"].to(device, non_blocking=True)
            freq = batch["freq"].to(device, non_blocking=True)
            y = batch["y"].to(device, non_blocking=True)
            mask = batch["mask"].to(device, non_blocking=True)
            mask_valid = batch["mask_valid"].to(device, non_blocking=True).view(-1)

            opt.zero_grad(set_to_none=True)

            with torch.cuda.amp.autocast(enabled=scaler.is_enabled()):
                out = model(rgb, freq)
                cls_logit = out["cls_logit"]
                mask_logit = out["mask_logit"]

                loss_cls = bce(cls_logit, y)

                # segmentation loss on valid subset only
                if mask_valid.any():
                    idx = mask_valid.nonzero(as_tuple=False).view(-1)
                    seg_logits = mask_logit[idx]
                    seg_targets = mask[idx]
                    loss_seg = bce(seg_logits, seg_targets) + dice_loss(seg_logits, seg_targets)
                else:
                    loss_seg = torch.tensor(0.0, device=device)

                loss = loss_cls + args.seg_weight * loss_seg

            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()

            loss_meter.append(float(loss.detach().cpu()))
            pbar.set_postfix(loss=np.mean(loss_meter))

        scheduler.step()

        metrics = evaluate(model, val_loader, device)
        auc, acc = metrics["auc"], metrics["acc"]
        print(f"[val] epoch={epoch} auc={auc:.4f} acc={acc:.4f}")

        # save best
        if auc > best_auc:
            best_auc = auc
            ckpt = {
                "model": model.state_dict(),
                "epoch": epoch,
                "best_auc": best_auc,
                "args": vars(args),
            }
            torch.save(ckpt, out_dir / "best.pt")

        torch.save({"model": model.state_dict(), "epoch": epoch}, out_dir / "last.pt")

    print("done. best_auc=", best_auc)

if __name__ == "__main__":
    main()
