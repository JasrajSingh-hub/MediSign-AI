"""Tests for model training/evaluation utilities (Phase 7).

Pure logic — CSV loading, stratified split, and metrics — runs offline.
scikit-learn-backed training is covered in ``test_training_integration.py``
(skipped when sklearn is absent).
"""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

import utils.model_utils as mu


# --------------------------------------------------------------------------
# Feature CSV loading (pure)
# --------------------------------------------------------------------------
def _write_features_csv(path: Path, rows, feature_cols=("f0", "f1", "f2")):
    cols = ["label", "video", "frame", "handedness", "score"] + list(feature_cols)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for label, feats in rows:
            row = {"label": label, "video": "v", "frame": "f", "handedness": "R", "score": 1.0}
            for c, v in zip(feature_cols, feats):
                row[c] = v
            w.writerow(row)


def test_load_features_csv():
    p = Path(tempfile.mkdtemp()) / "features.csv"
    _write_features_csv(p, [("help", [1, 2, 3]), ("pain", [4, 5, 6])])
    data = mu.load_features_csv(p)
    assert data["feature_names"] == ["f0", "f1", "f2"]
    assert data["X"] == [[1, 2, 3], [4, 5, 6]]
    assert data["y"] == ["help", "pain"]


def test_load_features_ignores_metadata_cols():
    p = Path(tempfile.mkdtemp()) / "features.csv"
    _write_features_csv(p, [("help", [1, 2, 3])])
    data = mu.load_features_csv(p)
    assert "label" not in data["feature_names"]
    assert "video" not in data["feature_names"]


# --------------------------------------------------------------------------
# Stratified split (pure)
# --------------------------------------------------------------------------
def test_stratified_split_sizes_and_balance():
    y = ["help"] * 5 + ["pain"] * 5
    X = [[i] for i in range(10)]
    X_tr, y_tr, X_te, y_te = mu.train_test_split_stratified(X, y, test_size=0.2, random_seed=42, stratify=True)
    assert len(X_te) == 2 and len(X_tr) == 8
    assert y_te.count("help") == 1 and y_te.count("pain") == 1  # balanced


def test_split_reproducible_with_seed():
    y = ["help"] * 5 + ["pain"] * 5
    X = [[i] for i in range(10)]
    a = mu.train_test_split_stratified(X, y, test_size=0.2, random_seed=42)
    b = mu.train_test_split_stratified(X, y, test_size=0.2, random_seed=42)
    assert a[1] == b[1]  # y_train identical


def test_split_differs_with_different_seed():
    y = ["help"] * 5 + ["pain"] * 5
    X = [[i] for i in range(10)]
    a = mu.train_test_split_stratified(X, y, test_size=0.2, random_seed=42)
    b = mu.train_test_split_stratified(X, y, test_size=0.2, random_seed=7)
    # very likely to differ; not guaranteed but strong for this data
    assert a[1] != b[1] or a[3] != b[3]


# --------------------------------------------------------------------------
# Metrics (pure)
# --------------------------------------------------------------------------
def test_classification_metrics_known_case():
    y_true = ["help", "help", "pain", "pain"]
    y_pred = ["help", "pain", "pain", "pain"]
    m = mu.classification_metrics(y_true, y_pred, ["help", "pain"])
    assert m["accuracy"] == pytest.approx(0.75)
    assert m["per_class"]["help"]["precision"] == pytest.approx(1.0)
    assert m["per_class"]["help"]["recall"] == pytest.approx(0.5)
    assert m["per_class"]["pain"]["recall"] == pytest.approx(1.0)
    assert m["confusion_matrix"]["help"]["pain"] == 1
    assert m["confusion_matrix"]["pain"]["pain"] == 2


def test_classification_metrics_perfect():
    y_true = ["a", "b", "c"]
    y_pred = ["a", "b", "c"]
    m = mu.classification_metrics(y_true, y_pred, ["a", "b", "c"])
    assert m["accuracy"] == 1.0
    assert m["macro_f1"] == pytest.approx(1.0)


# --------------------------------------------------------------------------
# Offline orchestration (sklearn absent -> graceful skip)
# --------------------------------------------------------------------------
def test_run_training_offline_skips():
    p = Path(tempfile.mkdtemp()) / "features.csv"
    _write_features_csv(p, [("help", [1, 2, 3]), ("pain", [4, 5, 6])])
    out_dir = Path(tempfile.mkdtemp())
    res = mu.run_training(features_csv=p, model_path=out_dir / "m.pkl", reports_dir=out_dir)
    assert res["skipped"] is True
    assert not (out_dir / "m.pkl").exists()


def test_run_training_missing_csv_skips():
    res = mu.run_training(features_csv=Path(tempfile.mkdtemp()) / "nope.csv", reports_dir=Path(tempfile.mkdtemp()))
    assert res["skipped"] is True
