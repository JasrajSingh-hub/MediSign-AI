import io
import os

import numpy as np
from PIL import Image, ImageFilter
import pytesseract

_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(_TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT


def _otsu_threshold(arr: np.ndarray) -> int:
    hist = np.bincount(arr.ravel(), minlength=256)
    total = arr.size
    sum_total = np.dot(np.arange(256), hist)
    sum_back, weight_back, max_var, threshold = 0.0, 0.0, 0.0, 0
    for t in range(256):
        weight_back += hist[t]
        if weight_back == 0:
            continue
        weight_fore = total - weight_back
        if weight_fore == 0:
            break
        sum_back += t * hist[t]
        mean_back = sum_back / weight_back
        mean_fore = (sum_total - sum_back) / weight_fore
        between = weight_back * weight_fore * (mean_back - mean_fore) ** 2
        if between > max_var:
            max_var = between
            threshold = t
    return threshold


def extract_text(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("L")
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    arr = np.array(img, dtype=np.uint8)
    thr = _otsu_threshold(arr)
    binarized = (arr > thr).astype(np.uint8) * 255
    img = Image.fromarray(binarized)
    img = img.filter(ImageFilter.MedianFilter(3))
    config = "--psm 6 --oem 3 -l eng"
    return pytesseract.image_to_string(img, config=config)

