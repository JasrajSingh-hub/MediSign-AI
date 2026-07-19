"""Image-to-prediction inference pipeline (Phase 9 glue).

Ties together MediaPipe landmark extraction (Phase 5), feature engineering
(Phase 6), and the singleton predictor (Phase 8) behind one function that takes
raw image bytes and returns a prediction dict. OpenCV and MediaPipe are imported
**lazily** so the module imports and its failure modes are testable without those
packages.
"""
from __future__ import annotations

from typing import Optional

import config
from utils.logger import get_logger
from utils import landmark_utils as lu
from utils import feature_utils as fu
from utils import predictor as pr

logger = get_logger(__name__)


def predict_from_image_bytes(
    image_bytes: bytes,
    predictor: Optional[pr.EmergencyPredictor] = None,
) -> dict:
    """Run the full pipeline on raw image bytes and return a prediction dict.

    Delegates to ModelManager singleton, but supports custom injected or monkeypatched
    predictors for test suites.
    """
    active_pred = predictor or pr.get_predictor()
    is_mock = not isinstance(active_pred, pr.EmergencyPredictor)

    if is_mock:
        try:
            import cv2
            import numpy as np
            from utils import landmark_utils as lu
            from utils import feature_utils as fu

            if not image_bytes:
                return {"available": False, "error": "Empty image bytes"}

            arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                return {"available": False, "error": "Could not decode image bytes"}

            lm_cfg = config.CONFIG["landmarks"]
            hands = lu.create_hands(lm_cfg)
            try:
                detections = lu.detect_landmarks(img, hands)
                if not detections:
                    return {"available": False, "error": "No hand detected in image"}
                xyz = detections[0]["xyz"]
            finally:
                try:
                    hands.close()
                except Exception:
                    pass

            flat = lu.normalize_landmarks(xyz, normalize=bool(lm_cfg.get("normalize_landmarks", True)))
            feats = fu.build_feature_vector(flat)
            return active_pred.is_emergency(feats)
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    from utils.model_manager import get_model_manager
    manager = get_model_manager()
    return manager.predict_emergency(image_bytes)
