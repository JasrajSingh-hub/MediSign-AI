"""Coverage tests for the runnable batch ``scripts/`` (Phase 10 backfill).

Each script is a thin wrapper around a utility function. We exercise ``main()``
with the underlying utility mocked (so no heavy decoding/training runs) and the
dependency guards by forcing the relevant imports to fail.
"""
from __future__ import annotations

import csv
import sys

import pytest

import scripts.analyze_dataset as ad
import scripts.extract_frames as ef
import scripts.extract_landmarks as el
import scripts.feature_engineering as fe
import scripts.predict as pr
import scripts.process_images as pi
import scripts.train as tr


# --------------------------------------------------------------------------
# extract_frames
# --------------------------------------------------------------------------
def test_extract_frames_main(monkeypatch, capsys):
    monkeypatch.setattr(ef, "extract_dataset_frames", lambda **kw: {"summary": {"total_videos": 3}})
    ef.main()
    assert "total_videos" in capsys.readouterr().out


def test_extract_frames_requires_cv2(monkeypatch):
    monkeypatch.setitem(sys.modules, "cv2", None)
    with pytest.raises(SystemExit):
        ef._require_cv2()


# --------------------------------------------------------------------------
# process_images
# --------------------------------------------------------------------------
def test_process_images_main(monkeypatch, capsys):
    monkeypatch.setattr(pi, "process_dataset_images", lambda **kw: {"summary": {"processed": 5}})
    pi.main()
    assert "processed" in capsys.readouterr().out


def test_process_images_requires_cv2(monkeypatch):
    monkeypatch.setitem(sys.modules, "cv2", None)
    with pytest.raises(SystemExit):
        pi._require_cv2()


# --------------------------------------------------------------------------
# extract_landmarks
# --------------------------------------------------------------------------
def test_extract_landmarks_main(monkeypatch, capsys):
    monkeypatch.setattr(el, "extract_dataset_landmarks", lambda **kw: {"summary": {"detected": 7}})
    el.main()
    assert "detected" in capsys.readouterr().out


def test_extract_landmarks_requires_deps(monkeypatch):
    monkeypatch.setitem(sys.modules, "mediapipe", None)
    monkeypatch.setitem(sys.modules, "cv2", None)
    with pytest.raises(SystemExit):
        el._require_deps()


# --------------------------------------------------------------------------
# feature_engineering
# --------------------------------------------------------------------------
def test_feature_engineering_main(monkeypatch, capsys):
    monkeypatch.setattr(fe, "run_feature_engineering", lambda **kw: {"rows": 9, "engineered_feature_count": 231, "total_feature_count": 294})
    fe.main()
    assert "rows" in capsys.readouterr().out


# --------------------------------------------------------------------------
# train
# --------------------------------------------------------------------------
def test_train_main(monkeypatch, capsys):
    monkeypatch.setattr(tr, "run_training", lambda **kw: {"train_size": 10, "test_size": 2, "skipped": False, "evaluation": {"accuracy": 0.9, "macro_f1": 0.9}})
    tr.main()
    assert "train_size" in capsys.readouterr().out


def test_train_requires_sklearn(monkeypatch):
    monkeypatch.setitem(sys.modules, "sklearn", None)
    monkeypatch.setitem(sys.modules, "joblib", None)
    with pytest.raises(SystemExit):
        tr._require_sklearn()


# --------------------------------------------------------------------------
# predict (CLI)
# --------------------------------------------------------------------------
def _write_features_csv(path, cols=("label", "video", "frame", "handedness", "score", "f0", "f1")):
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerow({**{c: "" for c in cols}, "label": "help", "f0": 1.0, "f1": 2.0})


def test_predict_main_success(monkeypatch, tmp_path):
    feat = tmp_path / "features.csv"
    _write_features_csv(feat)

    class _P:
        def ensure_loaded(self):
            return True

        def predict(self, X):
            return {"label": "help", "confidence": 0.9, "probabilities": {}, "available": True}

    monkeypatch.setattr(pr, "get_predictor", staticmethod(lambda *a, **k: _P()))
    monkeypatch.setattr(sys, "argv", ["predict.py", str(feat)])
    pr.main()  # should not raise


def test_predict_main_no_model(monkeypatch, tmp_path):
    feat = tmp_path / "features.csv"
    _write_features_csv(feat)

    class _P:
        def ensure_loaded(self):
            return False

    monkeypatch.setattr(pr, "get_predictor", staticmethod(lambda *a, **k: _P()))
    monkeypatch.setattr(sys, "argv", ["predict.py", str(feat)])
    with pytest.raises(SystemExit):
        pr.main()


def test_predict_main_missing_csv(monkeypatch, tmp_path):
    class _P:
        def ensure_loaded(self):
            return True

    monkeypatch.setattr(pr, "get_predictor", staticmethod(lambda *a, **k: _P()))
    monkeypatch.setattr(sys, "argv", ["predict.py", str(tmp_path / "nope.csv")])
    with pytest.raises(SystemExit):
        pr.main()


# --------------------------------------------------------------------------
# analyze_dataset
# --------------------------------------------------------------------------
def test_analyze_dataset_main(monkeypatch, capsys):
    fake_report = {"summary": {"total_videos": 624, "classes_count": 6, "total_size_bytes": 2_700_000_000, "corrupted_count": 0}}
    monkeypatch.setattr(ad, "analyze", lambda **kw: fake_report)
    ad.main()
    assert "total_videos" in capsys.readouterr().out
