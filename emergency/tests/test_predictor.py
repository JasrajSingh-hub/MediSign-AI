"""Tests for the prediction engine (Phase 8).

Offline: a stub model can be injected into ``EmergencyPredictor`` so the full
prediction/confidence/probabilities logic is exercised without scikit-learn.
"""
from __future__ import annotations

import pytest

import utils.predictor as pr


class _StubModel:
    classes_ = ["help", "pain"]

    def predict(self, X):
        return ["help"]

    def predict_proba(self, X):
        return [[0.8, 0.2]]


class _StubModelAlt:
    classes_ = ["help", "pain"]

    def predict(self, X):
        return ["pain"]

    def predict_proba(self, X):
        return [[0.1, 0.9]]


def _open_hand_xyz():
    wrist = [0.0, 0.0, 0.0]
    thumb = [[0.1, 0.05, 0], [0.2, 0.05, 0], [0.3, 0.05, 0], [0.4, 0.05, 0]]
    index = [[0, 0.15, 0], [0, 0.30, 0], [0, 0.45, 0], [0, 0.60, 0]]
    middle = [[0, 0.20, 0], [0, 0.35, 0], [0, 0.50, 0], [0, 0.65, 0]]
    ring = [[0, 0.15, 0], [0, 0.30, 0], [0, 0.45, 0], [0, 0.60, 0]]
    pinky = [[0, 0.10, 0], [0, 0.25, 0], [0, 0.40, 0], [0, 0.55, 0]]
    return [wrist] + thumb + index + middle + ring + pinky


def test_loaded_via_injection():
    p = pr.EmergencyPredictor(model=_StubModel(), classes=["help", "pain"])
    assert p.is_loaded is True


def test_predict_returns_label_confidence_probs():
    p = pr.EmergencyPredictor(model=_StubModel(), classes=["help", "pain"])
    res = p.predict([0.0] * 294)
    assert res["label"] == "help"
    assert res["confidence"] == pytest.approx(0.8)
    assert res["probabilities"] == {"help": 0.8, "pain": 0.2}
    assert res["available"] is True


def test_predict_argmax_chosen():
    p = pr.EmergencyPredictor(model=_StubModelAlt(), classes=["help", "pain"])
    res = p.predict([0.0] * 294)
    assert res["label"] == "pain"
    assert res["confidence"] == pytest.approx(0.9)


def test_predict_from_xyz_uses_features():
    p = pr.EmergencyPredictor(model=_StubModel(), classes=["help", "pain"])
    res = p.predict_from_xyz(_open_hand_xyz())
    assert res["label"] == "help"
    assert res["available"] is True


def test_predict_without_model_raises():
    p = pr.EmergencyPredictor(model_path="nonexistent.pkl")  # no model, no file
    assert p.is_loaded is False
    with pytest.raises(RuntimeError):
        p.predict([0.0] * 294)


def test_is_emergency_threshold():
    p = pr.EmergencyPredictor(model=_StubModel(), classes=["help", "pain"])
    res = p.is_emergency([0.0] * 294, threshold=0.5)
    assert res["is_emergency"] is True
    res2 = p.is_emergency([0.0] * 294, threshold=0.95)
    assert res2["is_emergency"] is False


def test_singleton_get_predictor():
    pr.reset_predictor()
    a = pr.get_predictor(model=_StubModel(), classes=["help", "pain"])
    b = pr.get_predictor()
    assert a is b
    pr.reset_predictor()
    c = pr.get_predictor(model=_StubModelAlt(), classes=["help", "pain"])
    assert c is not a
    pr.reset_predictor()
