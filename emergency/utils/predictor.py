"""Singleton prediction engine (Phase 8).

Wraps the trained emergency-gesture model behind a small, reusable engine:

* **Singleton** — ``get_predictor()`` returns one shared, lazily-loaded instance.
* **Prediction** — accepts a feature vector (or raw 21-landmark ``xyz``), returns
  the label, confidence, and per-class probabilities.
* **Confidence** — the max class probability is surfaced; an ``is_emergency``
  helper applies a configurable threshold.
* **Logging** — every prediction is logged with its label and confidence.

The model is loaded lazily so the engine imports and its logic is unit-testable
without scikit-learn (a model object can be injected for tests). When the real
model or its dependencies are absent, predictions fail with a clear error rather
than crashing the API.
"""
from __future__ import annotations

from pathlib import Path

import config
from config import PATHS
from config.constants import DEFAULT_CONFIDENCE_THRESHOLD
from utils.logger import get_logger
from utils import model_utils as mu

logger = get_logger(__name__)


class EmergencyPredictor:
    """Thin, dependency-light wrapper around a trained classifier."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        classes: list[str] | None = None,
        cfg: dict | None = None,
        model: object | None = None,
    ) -> None:
        self.cfg = cfg or config.CONFIG
        self.model_path = Path(model_path) if model_path else PATHS["models_dir"] / self.cfg["training"]["model_filename"]
        self._model = model
        self._classes = list(classes) if classes else None
        self._loaded = model is not None
        if model is not None and self._classes is None:
            cls = getattr(model, "classes_", None)
            self._classes = list(cls) if cls is not None else []

    # ------------------------------------------------------------------
    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def ensure_loaded(self) -> bool:
        """Load the model from disk if not already loaded. Returns success."""
        if self._loaded:
            return True
        if not self.model_path.exists():
            logger.warning("Emergency model not found at %s (run Phase 7 training).", self.model_path)
            return False
        try:
            self._model = mu.load_model(self.model_path)
            cls = getattr(self._model, "classes_", None)
            self._classes = list(cls) if cls is not None else []
            self._loaded = True
            logger.info("Loaded emergency model from %s", self.model_path)
            return True
        except ImportError as exc:
            logger.error("Cannot load model (scikit-learn/joblib missing): %s", exc)
            return False

    # ------------------------------------------------------------------
    def predict(self, features) -> dict:
        """Predict from a single feature vector.

        Returns ``{"label", "confidence", "probabilities", "available"}``.
        Raises ``RuntimeError`` if the model is not available.
        """
        if not self.ensure_loaded():
            raise RuntimeError("Emergency model is not loaded (train first / install dependencies).")
        X = [list(features)]
        preds, proba, classes = mu.predict(self._model, X)
        label = preds[0]
        probs = proba[0]
        prob_map = {c: float(p) for c, p in zip(classes, probs)}
        confidence = float(max(probs)) if len(probs) else 0.0
        self._log_prediction(label, confidence)
        return {"label": label, "confidence": confidence, "probabilities": prob_map, "available": True}

    def predict_from_xyz(self, xyz) -> dict:
        """Predict directly from 21 ``[x, y, z]`` landmarks."""
        from utils.feature_utils import build_feature_vector

        flat = [v for point in xyz for v in point]
        return self.predict(build_feature_vector(flat))

    def is_emergency(self, features, threshold: float | None = None) -> dict:
        """Predict and also flag whether confidence clears ``threshold``."""
        threshold = DEFAULT_CONFIDENCE_THRESHOLD if threshold is None else threshold
        result = self.predict(features)
        result["threshold"] = threshold
        result["is_emergency"] = result["confidence"] >= threshold
        return result

    def _log_prediction(self, label: str, confidence: float) -> None:
        logger.info("Prediction: %s (confidence=%.3f)", label, confidence)


_predictor: "EmergencyPredictor | None" = None


def get_predictor(
    model_path: str | Path | None = None,
    cfg: dict | None = None,
    model: object | None = None,
    classes: list[str] | None = None,
) -> EmergencyPredictor:
    """Return the shared singleton predictor (creating it on first call).

    Passing ``model`` injects a pre-built model (used by tests).
    """
    global _predictor
    if _predictor is None or model is not None:
        _predictor = EmergencyPredictor(model_path=model_path, cfg=cfg, model=model, classes=classes)
    return _predictor


def reset_predictor() -> None:
    """Drop the cached singleton (used by tests to avoid cross-test leakage)."""
    global _predictor
    _predictor = None
