"""Prediction CLI (Phase 8).

Loads the trained model and predicts the first data row of a features CSV. Run::

    python -m scripts.predict [path/to/features.csv]

Requires a trained model (Phase 7) and scikit-learn/joblib.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import PATHS
from utils.predictor import get_predictor
from utils.logger import get_logger

logger = get_logger("predict_cli")

_METADATA_COLS = ["label", "video", "frame", "handedness", "score"]


def main() -> None:
    features_csv = Path(sys.argv[1]) if len(sys.argv) > 1 else PATHS["landmarks_dir"] / "features.csv"
    predictor = get_predictor()
    if not predictor.ensure_loaded():
        logger.error("Model not loaded; train first (Phase 7) and install dependencies.")
        print("ERROR: emergency model not available. Run Phase 7 training and install deps.")
        sys.exit(1)

    if not features_csv.exists():
        print(f"ERROR: features CSV not found: {features_csv}")
        sys.exit(1)

    with features_csv.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        feat_names = [c for c in reader.fieldnames if c not in _METADATA_COLS]
        row = next(reader, None)
    if row is None:
        print("No data rows in features CSV.")
        return
    X = [float(row[c]) for c in feat_names]
    result = predictor.predict(X)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
