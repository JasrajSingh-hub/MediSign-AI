"""Landmark extraction script (Phase 5).

Runs MediaPipe Hands over the cleaned frames, normalises landmarks, and writes
``landmarks.csv`` (and ``.parquet`` when available) plus a report. Run::

    python -m scripts.extract_landmarks

Requires MediaPipe (and OpenCV). Exits with a clear message if missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.landmark_utils import extract_dataset_landmarks
from utils.logger import get_logger

logger = get_logger("landmark_extraction")


def _require_deps() -> None:
    try:
        import mediapipe  # noqa: F401
        import cv2  # noqa: F401
    except ImportError as exc:
        logger.error("MediaPipe/cv2 required for landmark extraction but missing: %s", exc)
        print(
            "ERROR: MediaPipe and OpenCV are required.\n"
            "       Install dependencies with: pip install -r emergency/requirements.txt"
        )
        sys.exit(1)


def main() -> None:
    _require_deps()
    logger.info("=== Phase 5: Landmark Extraction ===")
    manifest = extract_dataset_landmarks()
    print(json.dumps(manifest["summary"], indent=2, default=str))


if __name__ == "__main__":
    main()
