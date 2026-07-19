"""Feature engineering script (Phase 6).

Reads the Phase-5 ``landmarks.csv``, computes engineered features (distances,
angles, finger states, palm direction), and writes ``features.csv`` plus a
report. Pure-Python — no OpenCV/MediaPipe required. Run::

    python -m scripts.feature_engineering
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.feature_utils import run_feature_engineering
from utils.logger import get_logger

logger = get_logger("feature_engineering")


def main() -> None:
    logger.info("=== Phase 6: Feature Engineering ===")
    summary = run_feature_engineering()
    print(json.dumps(
        {
            "rows": summary.get("rows"),
            "engineered_feature_count": summary.get("engineered_feature_count"),
            "total_feature_count": summary.get("total_feature_count"),
            "skipped": summary.get("skipped", False),
        },
        indent=2,
        default=str,
    ))


if __name__ == "__main__":
    main()
