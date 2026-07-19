"""Dataset analysis script (Phase 2).

Scans the raw ``SOS/`` video dataset and writes ``dataset_report.md`` and
``dataset_report.json`` into the reports directory.

Run with::

    python -m scripts.analyze_dataset
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure the emergency module root is importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.dataset_utils import analyze
from utils.logger import get_logger

logger = get_logger("dataset_analysis")


def main() -> None:
    logger.info("=== Phase 2: Dataset Analysis ===")
    report = analyze()
    summary = report["summary"]
    logger.info(
        "Scan complete: %d videos across %d classes (%.1f MB, %d corrupted)",
        summary["total_videos"],
        summary["classes_count"],
        summary["total_size_bytes"] / (1024 * 1024),
        summary["corrupted_count"],
    )
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
