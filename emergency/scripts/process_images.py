"""Image processing script (Phase 4).

Cleans every extracted frame (resize, normalise, contrast, histogram
equalisation, denoise) and writes the results under ``output/processed/``. Run::

    python -m scripts.process_images

Requires OpenCV (``cv2``); exits with a clear message if it is missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.image_utils import process_dataset_images
from utils.logger import get_logger

logger = get_logger("image_processing")


def _require_cv2() -> None:
    try:
        import cv2  # noqa: F401
    except ImportError:
        logger.error("OpenCV ('cv2') is required for image processing but is not installed.")
        print(
            "ERROR: OpenCV ('cv2') is not installed.\n"
            "       Install dependencies with: pip install -r emergency/requirements.txt"
        )
        sys.exit(1)


def main() -> None:
    _require_cv2()
    logger.info("=== Phase 4: Image Processing ===")
    manifest = process_dataset_images()
    print(json.dumps(manifest["summary"], indent=2, default=str))


if __name__ == "__main__":
    main()
