"""Coverage for the full inference pipeline happy + no-hand paths (Phase 10)."""
from __future__ import annotations

import numpy as np
import pytest

import utils.inference as inf
import utils.landmark_utils as lu


def _fake_hand():
    return {"handedness": "Right", "score": 0.9, "xyz": [[0.0, 0.0, 0.0]] + [[0.1, 0.1, 0.0]] * 20}


class _FakePredictor:
    def is_emergency(self, feats):
        return {"available": True, "label": "help", "confidence": 0.9, "is_emergency": True}


def test_predict_happy_path(monkeypatch):
    monkeypatch.setattr("cv2.imdecode", lambda arr, flag: np.zeros((10, 10, 3), dtype=np.uint8))
    monkeypatch.setattr(lu, "create_hands", lambda p: object())
    monkeypatch.setattr(lu, "detect_landmarks", lambda img, hands: [_fake_hand()])
    monkeypatch.setattr(inf.pr, "get_predictor", staticmethod(lambda *a, **k: _FakePredictor()))

    res = inf.predict_from_image_bytes(b"some-image-bytes")
    assert res["available"] is True
    assert res["label"] == "help"
    assert res["confidence"] == pytest.approx(0.9)


def test_predict_no_hand(monkeypatch):
    monkeypatch.setattr("cv2.imdecode", lambda arr, flag: np.zeros((10, 10, 3), dtype=np.uint8))
    monkeypatch.setattr(lu, "create_hands", lambda p: object())
    monkeypatch.setattr(lu, "detect_landmarks", lambda img, hands: [])

    res = inf.predict_from_image_bytes(b"some-image-bytes")
    assert res["available"] is False
    assert "No hand" in res["error"]


def test_predict_model_unavailable(monkeypatch):
    monkeypatch.setattr("cv2.imdecode", lambda arr, flag: np.zeros((10, 10, 3), dtype=np.uint8))
    monkeypatch.setattr(lu, "create_hands", lambda p: object())
    monkeypatch.setattr(lu, "detect_landmarks", lambda img, hands: [_fake_hand()])

    class _UnavailablePredictor:
        def is_emergency(self, feats):
            raise RuntimeError("model not loaded")

    monkeypatch.setattr(inf.pr, "get_predictor", staticmethod(lambda *a, **k: _UnavailablePredictor()))

    res = inf.predict_from_image_bytes(b"some-image-bytes")
    assert res["available"] is False
