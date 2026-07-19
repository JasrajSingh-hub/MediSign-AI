"""Model Manager abstraction for MediSign-AI (Phase 1/Centralized AI).

Responsible for:
1. Singleton instantiation (`get_model_manager()`).
2. Lazy-loading of AI models (Sign Language RF, Emergency RF, MediaPipe Landmarker, OCR placeholders).
3. Running predictions for Sign Language and Emergency models using modern MediaPipe Tasks API.
4. Exposing metadata (version, accuracy, training dates, classes) for each model.
"""
from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config
from config import PATHS
from utils.logger import get_logger

logger = get_logger("model_manager")


class ModelManager:
    """Manages all machine learning models and inference pipelines for the application."""

    def __init__(self, cfg: Optional[Dict] = None) -> None:
        self.cfg = cfg or config.CONFIG
        
        # Resolve model paths
        self.emergency_path = PATHS["models_dir"] / self.cfg["training"]["model_filename"]
        self.sign_path = Path(self.cfg["api"]["sign_model_path"])
        # Resolve relative to repo root if path is relative
        if not self.sign_path.is_absolute():
            self.sign_path = PATHS["repo_root"] / self.sign_path

        self.landmarker_path = PATHS["models_dir"] / self.cfg["api"]["hand_landmarker_task_path"]

        # Models storage
        self._emergency_model: Any = None
        self._sign_model: Any = None
        self._landmarker: Any = None
        
        # Verification states
        self._loaded_emergency = False
        self._loaded_sign = False
        self._loaded_landmarker = False

    # -------------------------------------------------------------------------
    # Model Loaders
    # -------------------------------------------------------------------------
    def _load_model_file(self, path: Path) -> Any:
        """Load model using joblib if available, falling back to standard pickle."""
        try:
            import joblib
            return joblib.load(path)
        except Exception:
            with open(path, "rb") as fh:
                return pickle.load(fh)

    def load_emergency_model(self) -> bool:
        """Load the Emergency Random Forest model from disk."""
        if self._loaded_emergency:
            return True
        if not self.emergency_path.exists():
            logger.warning("Emergency model not found at %s. Please train Phase 7 first.", self.emergency_path)
            return False
        try:
            self._emergency_model = self._load_model_file(self.emergency_path)
            self._loaded_emergency = True
            logger.info("Loaded Emergency model from %s", self.emergency_path)
            return True
        except Exception as exc:
            logger.error("Failed to load Emergency model: %s", exc)
            return False

    def load_sign_model(self) -> bool:
        """Load the Sign Language Random Forest model from disk."""
        if self._loaded_sign:
            return True
        if not self.sign_path.exists():
            logger.warning("Sign language model not found at %s.", self.sign_path)
            return False
        try:
            self._sign_model = self._load_model_file(self.sign_path)
            self._loaded_sign = True
            logger.info("Loaded Sign Language model from %s", self.sign_path)
            return True
        except Exception as exc:
            logger.error("Failed to load Sign Language model: %s", exc)
            return False

    def load_landmarker(self) -> bool:
        """Load/Initialize MediaPipe HandLandmarker Tasks model."""
        if self._loaded_landmarker:
            return True
        try:
            from utils.landmark_utils import create_hands
            lm_cfg = dict(self.cfg["landmarks"])
            # Override model path in config for the landmarker
            lm_cfg["model_path"] = str(self.landmarker_path)
            self._landmarker = create_hands(lm_cfg)
            self._loaded_landmarker = True
            logger.info("Loaded MediaPipe HandLandmarker from %s", self.landmarker_path)
            return True
        except Exception as exc:
            logger.error("Failed to initialize HandLandmarker: %s", exc)
            return False

    def load_all_models(self) -> Dict[str, bool]:
        """Attempt to load all models, returning a summary of successes."""
        return {
            "emergency": self.load_emergency_model(),
            "sign": self.load_sign_model(),
            "landmarker": self.load_landmarker(),
        }

    # -------------------------------------------------------------------------
    # Metadata Exposer
    # -------------------------------------------------------------------------
    def get_metadata(self) -> Dict[str, Any]:
        """Expose version and metadata metrics for all managed models."""
        # Get active classes if models are loaded
        sign_classes = []
        if self.load_sign_model() and self._sign_model:
            sign_classes = list(getattr(self._sign_model, "classes_", []))
            # Convert NumPy types to serializable Python lists
            sign_classes = [str(c) for c in sign_classes]
            
        emergency_classes = []
        if self.load_emergency_model() and self._emergency_model:
            emergency_classes = list(getattr(self._emergency_model, "classes_", []))
            emergency_classes = [str(c) for c in emergency_classes]

        return {
            "version": self.cfg["project"]["version"],
            "models": {
                "hand_landmarker": {
                    "name": "MediaPipe HandLandmarker (Tasks API)",
                    "loaded": self._loaded_landmarker,
                    "model_path": str(self.landmarker_path),
                    "version": "0.10.10",
                },
                "sign_language": {
                    "name": "Indian Sign Language Letter Recognition Model",
                    "loaded": self._loaded_sign,
                    "model_path": str(self.sign_path),
                    "version": "1.0.0",
                    "accuracy": 0.9200,
                    "training_date": "2026-07-16",
                    "classes": sign_classes or list(self.cfg["dataset"].get("sign_classes", [])),
                },
                "emergency": {
                    "name": "MediSign-AI Emergency Gesture Recognition Model",
                    "loaded": self._loaded_emergency,
                    "model_path": str(self.emergency_path),
                    "version": "0.1.0",
                    "accuracy": 0.9581,
                    "training_date": "2026-07-17",
                    "classes": emergency_classes or list(self.cfg["dataset"]["classes"]),
                },
                "ocr": {
                    "name": "Prescription OCR Engine (Tesseract/Placeholder)",
                    "loaded": True, # Always ready (stubbed for Phase 2)
                    "version": "0.1.0-MVP",
                    "classes": ["Hospital", "Doctor", "Patient", "Medicines"],
                }
            }
        }

    # -------------------------------------------------------------------------
    # Inference Pipelines
    # -------------------------------------------------------------------------
    def predict_sign(self, image_bytes: bytes) -> Dict[str, Any]:
        """Inference pipeline for Sign Language letter prediction.

        Accepts raw image bytes, runs landmarker, and runs Sign Random Forest.
        """
        if not self.load_sign_model():
            return {"available": False, "error": "Sign Language model not loaded on server."}
        if not self.load_landmarker():
            return {"available": False, "error": "Hand Landmarker not loaded on server."}

        # 1. Decode image bytes
        img = self._decode_image(image_bytes)
        if img is None:
            return {"available": False, "error": "Could not decode image bytes."}

        # 2. Extract landmarks using Tasks API
        from utils.landmark_utils import detect_landmarks
        try:
            detections = detect_landmarks(img, self._landmarker)
        except Exception as exc:
            return {"available": False, "error": f"MediaPipe error: {exc}"}

        if not detections:
            return {"letter": "No hand", "confidence": "0%", "available": True}

        # 3. Build features (extract_hand & normalize from app.py)
        try:
            data_row = self._build_sign_features(detections)
            if len(data_row) != 126:
                return {"letter": "Error", "confidence": "0%", "available": True, "error": "Invalid feature length"}
            
            # Normalize
            data_row = self._normalize_sign_row(data_row)
            
            # 4. Predict
            prediction = self._sign_model.predict([data_row])[0]
            proba = self._sign_model.predict_proba([data_row])[0]
            confidence = max(proba) * 100

            return {
                "letter": str(prediction),
                "confidence": f"{confidence:.1f}%",
                "available": True
            }
        except Exception as exc:
            logger.error("Sign prediction failed: %s", exc)
            return {"available": False, "error": f"Prediction failed: {exc}"}

    def predict_emergency(self, image_bytes: bytes) -> Dict[str, Any]:
        """Inference pipeline for Emergency gesture prediction."""
        if not self.load_emergency_model():
            return {"available": False, "error": "Emergency model not loaded on server."}
        if not self.load_landmarker():
            return {"available": False, "error": "Hand Landmarker not loaded on server."}

        # 1. Decode image bytes
        img = self._decode_image(image_bytes)
        if img is None:
            return {"available": False, "error": "Could not decode image bytes."}

        # 2. Extract landmarks
        from utils.landmark_utils import detect_landmarks
        try:
            detections = detect_landmarks(img, self._landmarker)
        except Exception as exc:
            return {"available": False, "error": f"MediaPipe error: {exc}"}

        if not detections:
            return {"available": False, "error": "No hand detected in image."}

        # 3. Build features & predict
        try:
            from utils.landmark_utils import normalize_landmarks
            from utils.feature_utils import build_feature_vector

            xyz = detections[0]["xyz"]
            lm_cfg = self.cfg["landmarks"]
            flat = normalize_landmarks(xyz, normalize=bool(lm_cfg.get("normalize_landmarks", True)))
            feats = build_feature_vector(flat)
            
            # Run Random Forest
            preds = self._emergency_model.predict([feats])
            proba = self._emergency_model.predict_proba([feats])[0]
            classes = list(getattr(self._emergency_model, "classes_", []))
            
            label = preds[0]
            prob_map = {str(c): float(p) for c, p in zip(classes, proba)}
            confidence = float(max(proba))
            
            threshold = self.cfg["api"]["emergency_confidence_threshold"]
            is_emergency = confidence >= threshold

            return {
                "label": label,
                "confidence": confidence,
                "probabilities": prob_map,
                "is_emergency": is_emergency,
                "available": True
            }
        except Exception as exc:
            logger.error("Emergency prediction failed: %s", exc)
            return {"available": False, "error": f"Prediction failed: {exc}"}

    # -------------------------------------------------------------------------
    # Helper utilities
    # -------------------------------------------------------------------------
    def _decode_image(self, image_bytes: bytes) -> Any:
        import cv2
        import numpy as np
        if not image_bytes:
            return None
        arr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    def _build_sign_features(self, detections: List[Dict[str, Any]]) -> List[float]:
        """Replicates Flask app.py hand landmark structuring with Tasks API outputs."""
        def extract_hand_xyz(xyz):
            wx, wy, wz = xyz[0][0], xyz[0][1], xyz[0][2]
            row = []
            for p in xyz:
                row.extend([p[0] - wx, p[1] - wy, p[2] - wz])
            return row

        data_row = []
        num_hands = len(detections)

        if num_hands >= 2:
            # Sort by handedness label: 'Left' comes before 'Right' alphabetically
            detections_sorted = sorted(detections[:2], key=lambda x: x["handedness"])
            for d in detections_sorted:
                data_row.extend(extract_hand_xyz(d["xyz"]))
        elif num_hands == 1:
            d = detections[0]
            hand_data = extract_hand_xyz(d["xyz"])
            if d["handedness"] == 'Left':
                data_row = hand_data + [0] * 63
            else:
                data_row = [0] * 63 + hand_data
        return data_row

    def _normalize_sign_row(self, landmarks_relative: List[float]) -> List[float]:
        """Replicates Flask app.py normalisation logic."""
        xs = landmarks_relative[0::3]
        ys = landmarks_relative[1::3]
        scale = max(max(xs) - min(xs), max(ys) - min(ys))
        if scale == 0:
            return landmarks_relative
        return [v / scale for v in landmarks_relative]


# Singleton instance
_model_manager: ModelManager | None = None


def get_model_manager(cfg: Optional[Dict] = None) -> ModelManager:
    """Get or create the singleton ModelManager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(cfg=cfg)
    return _model_manager


def reset_model_manager() -> None:
    """Reset the singleton instance (used for clean testing states)."""
    global _model_manager
    _model_manager = None
