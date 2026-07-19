"""Frame extraction script (Phase 3).

Reads every AVI in the dataset, samples frames, skips corrupted videos, and
writes a ``manifest.json`` describing what was extracted. Run with::

    python -m scripts.extract_frames

Requires OpenCV (``cv2``); exits with a clear message if it is missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.video_utils import extract_dataset_frames
from utils.logger import get_logger

logger = get_logger("frame_extraction")


def _require_cv2() -> None:
    try:
        import cv2  # noqa: F401
    except ImportError:
        logger.error("OpenCV ('cv2') is required for frame extraction but is not installed.")
        print(
            "ERROR: OpenCV ('cv2') is not installed.\n"
            "       Install dependencies with: pip install -r emergency/requirements.txt"
        )
        sys.exit(1)


def main() -> None:
    _require_cv2()
    logger.info("=== Phase 3: Frame Extraction ===")
    manifest = extract_dataset_frames()
    print(json.dumps(manifest["summary"], indent=2, default=str))


if __name__ == "__main__":
    main()
