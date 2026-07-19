"""Training script (Phase 7).

Loads ``features.csv``, runs cross-validation (and optional grid search), trains
a RandomForest, evaluates on the held-out test set, and saves
``models/emergency_model.pkl``. Run::

    python -m scripts.train

Requires scikit-learn and joblib. Exits with a clear message if missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.model_utils import run_training
from utils.logger import get_logger

logger = get_logger("training")


def _require_sklearn() -> None:
    try:
        import sklearn  # noqa: F401
        import joblib  # noqa: F401
    except ImportError as exc:
        logger.error("scikit-learn/joblib required for training but missing: %s", exc)
        print(
            "ERROR: scikit-learn and joblib are required.\n"
            "       Install dependencies with: pip install -r emergency/requirements.txt"
        )
        sys.exit(1)


def main() -> None:
    _require_sklearn()
    logger.info("=== Phase 7: Training ===")
    res = run_training()
    print(json.dumps(
        {"train_size": res.get("train_size"), "test_size": res.get("test_size"), "skipped": res.get("skipped", False)},
        indent=2,
        default=str,
    ))
    if "evaluation" in res:
        ev = res["evaluation"]
        print(f"Accuracy: {ev['accuracy']:.4f} | Macro-F1: {ev['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
