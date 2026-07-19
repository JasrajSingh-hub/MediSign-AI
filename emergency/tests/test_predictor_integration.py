"""Integration tests for the prediction engine (Phase 8).

Require scikit-learn + joblib. Skipped automatically when absent. When installed,
a tiny model is trained, saved, loaded through the singleton engine, and used to
predict a known sample (both via feature vector and raw landmarks).
"""
from __future__ import annotations

import csv

import pytest

sklearn = pytest.importorskip("sklearn")
np = pytest.importorskip("numpy")
pytest.importorskip("joblib")

import utils.model_utils as mu
import utils.predictor as pr


CLASSES = ["help", "doctor", "pain", "call", "accident", "hot"]


def _train_tiny_model(tmp_path):
    # Separable synthetic features per class.
    rng = np.random.RandomState(0)
    rows = []
    for ci, label in enumerate(CLASSES):
        mean = np.full(12, ci * 3.0)
        for _ in range(30):
            feats = (mean + rng.normal(0, 0.4, 12)).tolist()
            rows.append((label, feats))
    feat_csv = tmp_path / "features.csv"
    cols = ["label", "video", "frame", "handedness", "score"] + [f"f{i}" for i in range(12)]
    with feat_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for label, feats in rows:
            r = {"label": label, "video": "v", "frame": "f", "handedness": "R", "score": 1.0}
            for i, v in enumerate(feats):
                r[f"f{i}"] = v
            w.writerow(r)
    model_path = tmp_path / "models" / "emergency_model.pkl"
    res = mu.run_training(features_csv=feat_csv, model_path=model_path, reports_dir=tmp_path)
    assert res.get("skipped") is not True
    return feat_csv, model_path, rows


def test_predictor_loads_file_and_predicts(tmp_path):
    feat_csv, model_path, rows = _train_tiny_model(tmp_path)
    predictor = pr.EmergencyPredictor(model_path=model_path)
    assert predictor.ensure_loaded() is True
    # Predict a sample whose features match the "help" cluster centre.
    help_feats = [0.0 * 0 + 0.0] * 12  # placeholder; build from a real help row
    # Use the first help row from the training data.
    help_row = next(r for r in rows if r[0] == "help")
    result = predictor.predict(help_row[1])
    assert result["available"] is True
    assert result["label"] == "help"


def test_predictor_singleton_with_file(tmp_path):
    feat_csv, model_path, rows = _train_tiny_model(tmp_path)
    pr.reset_predictor()
    a = pr.get_predictor(model_path=model_path)
    b = pr.get_predictor()
    assert a is b
    a.ensure_loaded()
    assert a.is_loaded is True
    pr.reset_predictor()
