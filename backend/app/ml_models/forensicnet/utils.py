
import cv2
import numpy as np

def compute_ela_rgb(img_rgb: np.ndarray, quality: int = 95) -> np.ndarray:
    """
    Error Level Analysis (ELA)
    - img_rgb: uint8 RGB, shape(H,W,3)
    - returns: float32 RGB in [0,1], shape(H,W,3)
    """
    quality = int(np.clip(quality, 50, 100))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    # OpenCV expects BGR for imencode; we can convert
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    ok, enc = cv2.imencode(".jpg", img_bgr, encode_param)
    if not ok:
        raise RuntimeError("cv2.imencode failed for ELA")
    dec = cv2.imdecode(enc, cv2.IMREAD_COLOR)  # BGR
    dec_rgb = cv2.cvtColor(dec, cv2.COLOR_BGR2RGB)

    diff = cv2.absdiff(img_rgb, dec_rgb).astype(np.float32)  # 0..255
    # amplify for visibility; common trick
    diff = diff * (255.0 / max(1.0, diff.max()))
    diff = np.clip(diff, 0, 255) / 255.0
    return diff.astype(np.float32)

def compute_fft_mag(gray: np.ndarray) -> np.ndarray:
    """
    FFT magnitude map (log amplitude), standardized per-image.
    - gray: float32 in [0,1], shape(H,W)
    - returns: float32 standardized, shape(H,W)
    """
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = np.log1p(np.abs(fshift)).astype(np.float32)
    mag = (mag - mag.mean()) / (mag.std() + 1e-6)
    return mag

def rgb_to_gray01(img_rgb: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    return gray

def minmax01(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)
    mn, mx = float(x.min()), float(x.max())
    if mx - mn < 1e-6:
        return np.zeros_like(x, dtype=np.float32)
    return (x - mn) / (mx - mn)

