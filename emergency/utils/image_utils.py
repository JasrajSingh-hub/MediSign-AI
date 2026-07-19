"""Image pre-processing utilities (Phase 4).

Cleans extracted frames before landmark extraction: resize, intensity
normalisation, CLAHE contrast, histogram equalisation, and non-local-means
noise reduction. Every transform imports OpenCV **lazily**, so this module
imports (and its pure planning/orchestration logic is testable) without cv2.

All transforms keep the image as ``uint8`` BGR so the result remains directly
usable by MediaPipe Hands in Phase 5.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

import config
from config import PATHS
from utils.io_utils import ensure_dir
from utils.logger import get_logger
from utils.progress import tqdm

logger = get_logger(__name__)

# Fixed, sensible order. ``resize`` is always applied; the rest are config-gated.
_TRANSFORM_ORDER = ["resize", "contrast", "histogram_equalization", "noise_reduction", "normalize"]


def build_processing_plan(image_cfg: Optional[Dict] = None) -> List[str]:
    """Return the ordered list of transforms to apply, based on config flags.

    Parameters
    ----------
    image_cfg: The ``[image_processing]`` mapping. Defaults to the global config.

    Returns
    -------
    list[str]
        Transform names in execution order. ``resize`` is always present.
    """
    cfg = image_cfg if image_cfg is not None else config.CONFIG["image_processing"]
    plan: List[str] = ["resize"]
    if float(cfg.get("contrast_clip_limit", 0) or 0) > 0:
        plan.append("contrast")
    if cfg.get("histogram_equalization"):
        plan.append("histogram_equalization")
    if cfg.get("noise_reduction"):
        plan.append("noise_reduction")
    if cfg.get("normalize"):
        plan.append("normalize")
    return plan


# ---------------------------------------------------------------------------
# Individual transforms (each lazily imports OpenCV)
# ---------------------------------------------------------------------------
def resize_image(img, params: Dict) -> "object":
    import cv2

    size = tuple(int(v) for v in params.get("target_size", [256, 256]))
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)


def adjust_contrast(img, params: Dict) -> "object":
    """CLAHE contrast limited adaptive histogram equalisation on the L channel."""
    import cv2

    clip = float(params.get("contrast_clip_limit", 2.0))
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def equalize_histogram(img, params: Dict) -> "object":
    """Histogram equalisation on the luma (Y) channel to avoid colour shifts."""
    import cv2

    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = cv2.equalizeHist(y)
    return cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)


def denoise(img, params: Dict) -> "object":
    """Non-local means colour denoising."""
    import cv2

    h = int(params.get("denoise_strength", 7))
    return cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)


def normalize_image(img, params: Dict) -> "object":
    """Zero-mean / unit-variance standardisation, rescaled back to uint8.

    Keeps the output in the ``uint8`` BGR range so MediaPipe can consume it.
    """
    import numpy as np

    f = img.astype("float32")
    mean = f.mean()
    std = f.std() + 1e-6
    norm = (f - mean) / std
    norm = np.clip(norm * 64.0 + 128.0, 0, 255)
    return norm.astype("uint8")


_TRANSFORMS: Dict[str, Callable] = {
    "resize": resize_image,
    "contrast": adjust_contrast,
    "histogram_equalization": equalize_histogram,
    "noise_reduction": denoise,
    "normalize": normalize_image,
}


def process_frame(img, plan: List[str], params: Dict) -> "object":
    """Apply each transform in ``plan`` to ``img`` and return the result."""
    for name in plan:
        fn = _TRANSFORMS[name]
        img = fn(img, params)
    return img


def _gather_frames(frames_dir: Path) -> List[Path]:
    files: List[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        files.extend(frames_dir.rglob(ext))
    return sorted(files)


def process_dataset_images(
    frames_dir: Optional[str | Path] = None,
    out_dir: Optional[str | Path] = None,
    *,
    overwrite: bool = False,
    progress: bool = True,
    cfg: Optional[Dict] = None,
) -> Dict[str, object]:
    """Clean every extracted frame and write it under ``output/processed/``.

    Returns a summary dict and writes ``output/processed/manifest.json``. When
    OpenCV is unavailable each frame is reported as failed (rather than raising)
    so the batch still completes and downstream phases can detect the gap.
    """
    cfg = cfg or config.CONFIG
    frames_root = Path(frames_dir) if frames_dir else PATHS["frames_dir"]
    out_root = Path(out_dir) if out_dir else PATHS["processed_dir"]
    plan = build_processing_plan(cfg["image_processing"])
    params = dict(cfg["image_processing"])

    frame_files = _gather_frames(frames_root)
    processed = 0
    failed = 0
    skipped = 0
    failed_frames: List[str] = []

    iterator: List[Path] = frame_files
    if progress:
        iterator = tqdm(frame_files, desc="Processing frames", unit="frame")

    for src in iterator:
        try:
            rel = src.relative_to(frames_root)
        except ValueError:
            rel = Path(src.name)
        dest = out_root / rel
        if not overwrite and dest.exists():
            skipped += 1
            continue
        try:
            import cv2

            img = cv2.imread(str(src))
            if img is None:
                raise IOError(f"imread returned None for {src}")
            out = process_frame(img, plan, params)
            ensure_dir(dest.parent)
            if not cv2.imwrite(str(dest), out):
                raise IOError(f"imwrite failed for {dest}")
            processed += 1
        except Exception as exc:  # pragma: no cover - defensive; cv2 path
            failed += 1
            failed_frames.append(str(src))
            logger.warning("Failed to process %s: %s", src, exc)

    manifest = {
        "processing_plan": plan,
        "params": params,
        "frames_dir": str(frames_root),
        "processed_dir": str(out_root),
        "summary": {
            "total_frames": len(frame_files),
            "processed": processed,
            "failed": failed,
            "skipped": skipped,
        },
        "failed_frames": failed_frames,
    }
    ensure_dir(out_root)
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    logger.info(
        "Image processing complete: %d processed, %d failed, %d skipped",
        processed,
        failed,
        skipped,
    )
    return manifest
