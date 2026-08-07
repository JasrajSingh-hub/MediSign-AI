from __future__ import annotations

import base64
import math
import pickle
from pathlib import Path
from typing import Any, Optional

import cv2
try:
    import mediapipe as mp
except ImportError:
    mp = None
import numpy as np
from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "emergency_model.pkl"
LANDMARKER_PATH = BASE_DIR / "models" / "hand_landmarker.task"

_MODEL = None
_LANDMARKER = None


def _load_model() -> Any:
    try:
        import joblib

        return joblib.load(MODEL_PATH)
    except Exception:
        with MODEL_PATH.open("rb") as fh:
            return pickle.load(fh)


def _get_model() -> Any:
    global _MODEL
    if _MODEL is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"Emergency model not found at {MODEL_PATH}")
        _MODEL = _load_model()
    return _MODEL


def _get_landmarker() -> Any:
    global _LANDMARKER
    if _LANDMARKER is None:
        if not LANDMARKER_PATH.exists():
            raise RuntimeError(f"Hand landmarker not found at {LANDMARKER_PATH}")
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision

        base_options = mp_python.BaseOptions(model_asset_buffer=LANDMARKER_PATH.read_bytes())
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        _LANDMARKER = vision.HandLandmarker.create_from_options(options)
    return _LANDMARKER


def _decode_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    if not image_bytes:
        return None
    arr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _normalize_landmarks(xyz: list[list[float]]) -> list[float]:
    if not xyz:
        return [0.0] * 63
    wrist = xyz[0]
    centred = [[p[0] - wrist[0], p[1] - wrist[1], p[2] - wrist[2]] for p in xyz]
    xs = [p[0] for p in centred]
    ys = [p[1] for p in centred]
    scale = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    return [v / scale for point in centred for v in point]


def _dist(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _angle_at(b: list[float], a: list[float], c: list[float]) -> float:
    v1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
    v2 = [b[0] - c[0], b[1] - c[1], b[2] - c[2]]
    dot = sum(x * y for x, y in zip(v1, v2))
    n1 = _dist(b, a)
    n2 = _dist(b, c)
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    cos = max(-1.0, min(1.0, dot / (n1 * n2)))
    return math.acos(cos)


LANDMARK_PAIRS = [(i, j) for i in range(21) for j in range(i + 1, 21)]
ANGLE_TRIPLETS = [
    (0, 5, 8), (0, 9, 12), (0, 13, 16), (0, 17, 20),
    (1, 2, 3), (2, 3, 4), (5, 6, 7), (6, 7, 8),
    (9, 10, 11), (10, 11, 12), (13, 14, 15), (14, 15, 16), (17, 18, 19), (18, 19, 20),
]
FINGER_TIP = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
FINGER_PIP = {"thumb": 3, "index": 6, "middle": 10, "ring": 14, "pinky": 18}
FINGER_MCP = {"middle": 9}


def _engineer_features(xyz: list[list[float]]) -> list[float]:
    feats = []
    feats.extend(_dist(xyz[i], xyz[j]) for i, j in LANDMARK_PAIRS)
    feats.extend(_angle_at(xyz[b], xyz[a], xyz[c]) for a, b, c in ANGLE_TRIPLETS)
    wrist = xyz[0]
    for finger in ("thumb", "index", "middle", "ring", "pinky"):
        tip = xyz[FINGER_TIP[finger]]
        pip = xyz[FINGER_PIP[finger]]
        feats.append(1.0 if _dist(tip, wrist) > _dist(pip, wrist) else 0.0)
    middle_mcp = xyz[FINGER_MCP["middle"]]
    vx = middle_mcp[0] - wrist[0]
    vy = middle_mcp[1] - wrist[1]
    norm = math.sqrt(vx * vx + vy * vy) or 1.0
    feats.extend([vx / norm, vy / norm])
    return feats


def _build_features(xyz: list[list[float]]) -> list[float]:
    base = _normalize_landmarks(xyz)
    return base + _engineer_features([base[i:i + 3] for i in range(0, len(base), 3)])


def _detect_landmarks(image: np.ndarray) -> list[list[list[float]]]:
    landmarker = _get_landmarker()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)
    hands = result.hand_landmarks or []
    return [[[float(lm.x), float(lm.y), float(lm.z)] for lm in hand] for hand in hands]


def health() -> dict:
    return {"status": "ok", "model_loaded": MODEL_PATH.exists(), "landmarker_loaded": LANDMARKER_PATH.exists()}


def status() -> dict:
    model = _get_model()
    return {
        "status": "ok",
        "model_loaded": True,
        "model_path": str(MODEL_PATH),
        "classes": [str(c) for c in getattr(model, "classes_", [])],
    }


def predict(image_base64: Optional[str] = None, file_bytes: Optional[bytes] = None) -> dict:
    if file_bytes is not None:
        image_bytes = file_bytes
    elif image_base64:
        try:
            image_bytes = base64.b64decode(image_base64.split(",")[-1])
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {exc}")
    else:
        raise HTTPException(status_code=400, detail="Provide an image via file upload or image_base64.")

    image = _decode_image_bytes(image_bytes)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image bytes.")

    model = _get_model()
    hands = _detect_landmarks(image)
    if not hands:
        return {"available": True, "label": "No hand", "confidence": 0.0, "probabilities": {}, "is_emergency": False}

    xyz = hands[0]
    features = _build_features(xyz)
    preds = model.predict([features])
    proba = model.predict_proba([features])[0]
    classes = [str(c) for c in getattr(model, "classes_", [])]
    confidence = float(max(proba)) if len(proba) else 0.0
    return {
        "available": True,
        "label": str(preds[0]),
        "confidence": confidence,
        "probabilities": {c: float(p) for c, p in zip(classes, proba)},
        "is_emergency": confidence >= 0.5,
    }
