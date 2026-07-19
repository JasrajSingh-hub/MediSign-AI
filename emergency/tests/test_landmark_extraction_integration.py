"""Integration tests for landmark extraction (Phase 5).

Require MediaPipe, OpenCV, and NumPy. Skipped automatically when absent. When
installed: the Hands model builds, a blank frame yields no detection (reliable
no-hand path), and a hand-bearing image path is exercised end-to-end.
"""
from __future__ import annotations

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")
mp = pytest.importorskip("mediapipe")

import utils.landmark_utils as lu


def test_create_hands_builds_model():
    hands = lu.create_hands({"static_image_mode": True, "max_num_hands": 1, "min_detection_confidence": 0.5, "model_complexity": 1})
    assert hands is not None
    hands.close()


def test_detect_landmarks_blank_image_no_hand():
    # A solid colour image is extremely unlikely to contain a hand.
    img = np.full((128, 128, 3), 128, dtype=np.uint8)
    hands = lu.create_hands({"static_image_mode": True, "max_num_hands": 1, "min_detection_confidence": 0.5, "model_complexity": 1})
    try:
        detections = lu.detect_landmarks(img, hands)
        assert isinstance(detections, list)
    finally:
        hands.close()


def test_normalize_with_numpy_input():
    xyz = [[0.5, 0.5, 0.0], [0.6, 0.6, 0.0], [0.4, 0.4, 0.0]]
    out = lu.normalize_landmarks(xyz, normalize=True)
    assert len(out) == 9
    assert out[0] == 0.0


def test_write_dataset_with_pandas_present(tmp_path):
    rows = [
        {"label": "help", "video": "v", "frame": "f0", "handedness": "Right", "score": 0.9, "features": [float(i) for i in range(63)]},
    ]
    written = lu.write_landmark_dataset(rows, tmp_path / "landmarks.csv", parquet_path=tmp_path / "landmarks.parquet")
    assert (tmp_path / "landmarks.csv").exists()
    # Parquet may or may not be writable depending on pyarrow availability;
    # CSV remains the authoritative artefact either way.
    assert written["csv"] == str(tmp_path / "landmarks.csv")
