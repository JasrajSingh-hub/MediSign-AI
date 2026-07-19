"""Integration tests for training (Phase 7).

Require scikit-learn, joblib, and NumPy. Skipped automatically when absent.
When installed: a synthetic, class-separable features CSV is trained end-to-end,
the model is saved/loaded, and evaluation metrics are checked.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

sklearn = pytest.importorskip("sklearn")
np = pytest.importorskip("numpy")
pytest.importorskip("joblib")

import utils.model_utils as mu


N_FEATURES = 12
CLASSES = ["help", "doctor", "pain", "call", "accident", "hot"]


def _make_features_csv(path: Path, per_class: int = 40, seed: int = 0) -> None:
    rng = np.random.RandomState(seed)
    cols = ["label", "video", "frame", "handedness", "score"] + [f"f{i}" for i in range(N_FEATURES)]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for ci, label in enumerate(CLASSES):
            mean = np.full(N_FEATURES, ci * 3.0)  # well-separated cluster centres
            for _ in range(per_class):
                feats = (mean + rng.normal(0, 0.5, N_FEATURES)).tolist()
                row = {"label": label, "video": "v", "frame": "f", "handedness": "R", "score": 1.0}
                for i, v in enumerate(feats):
                    row[f"f{i}"] = v
                w.writerow(row)


def test_cross_validate_returns_summary(tmp_path):
    p = tmp_path / "features.csv"
    _make_features_csv(p)
    data = mu.load_features_csv(p)
    X_tr, y_tr, X_te, y_te = mu.train_test_split_stratified(data["X"], data["y"], test_size=0.2, random_seed=42)
    cv = mu.cross_validate(X_tr, y_tr, {"n_estimators": 50, "max_depth": 10, "min_samples_leaf": 1, "random_state": 42}, n_splits=3, seed=42)
    assert "mean" in cv and "folds" in cv
    assert len(cv["folds"]) == 3


def test_grid_search_runs(tmp_path):
    p = tmp_path / "features.csv"
    _make_features_csv(p, per_class=20)
    data = mu.load_features_csv(p)
    X_tr, y_tr, _, _ = mu.train_test_split_stratified(data["X"], data["y"], test_size=0.2, random_seed=42)
    model, best_params, info = mu.grid_search(X_tr, y_tr, {"n_estimators": [50, 100], "max_depth": [5, 10], "min_samples_leaf": [1, 2]}, n_splits=2, seed=42)
    assert hasattr(model, "predict")
    assert "n_estimators" in best_params


def test_end_to_end_training_saves_and_scores(tmp_path):
    p = tmp_path / "features.csv"
    _make_features_csv(p)
    model_path = tmp_path / "models" / "emergency_model.pkl"
    res = mu.run_training(features_csv=p, model_path=model_path, reports_dir=tmp_path, cfg=_fast_cfg())
    assert res["skipped"] is not True
    assert model_path.exists()
    assert "evaluation" in res
    # Synthetic clusters are easily separable -> strong performance.
    assert res["evaluation"]["accuracy"] > 0.8
    assert (tmp_path / "training_report.json").exists()

    # Model reload + predict consistency.
    loaded = mu.load_model(model_path)
    preds, proba, classes = mu.predict(loaded, res and mu.load_features_csv(p)["X"][:5])
    assert len(preds) == 5
    assert proba and len(proba[0]) == len(classes)


def _fast_cfg():
    import config

    cfg = json.loads(json.dumps(config.CONFIG))  # deep copy
    cfg["training"]["n_estimators"] = 50
    cfg["training"]["grid_search"] = False
    cfg["training"]["n_splits_cv"] = 3
    return cfg
