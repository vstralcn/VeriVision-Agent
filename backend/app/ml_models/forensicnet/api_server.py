
from __future__ import annotations
import os
import base64
import io
from typing import Optional

import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from .infer import load_model, predict

app = FastAPI(title="ForensicNet API", version="0.1")

CKPT_PATH = os.environ.get("FORENSICNET_CKPT", "runs/exp1/best.pt")
DEVICE = os.environ.get("FORENSICNET_DEVICE", "cpu")

_model = None

@app.on_event("startup")
def _startup():
    global _model
    if not os.path.exists(CKPT_PATH):
        print(f"[WARN] CKPT not found: {CKPT_PATH}. Set env FORENSICNET_CKPT to your path.")
        _model = None
    else:
        _model = load_model(CKPT_PATH, device=DEVICE)
        print(f"[OK] Loaded model from {CKPT_PATH} on {DEVICE}")

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...), return_mask: bool = True):
    if _model is None:
        return JSONResponse(status_code=500, content={"error": "Model not loaded. Check FORENSICNET_CKPT path."})
    image_bytes = await file.read()
    res = predict(_model, image_bytes, device=DEVICE, return_mask=return_mask)

    out = {
        "fake_prob": float(res.fake_prob),
        "label": "fake" if res.fake_prob >= 0.5 else "real",
    }
    if return_mask and res.mask_prob is not None:
        # compress mask as base64 npy to avoid huge json; frontend can decode
        buf = io.BytesIO()
        np.save(buf, res.mask_prob)
        out["mask_npy_b64"] = base64.b64encode(buf.getvalue()).decode("ascii")
    return out
