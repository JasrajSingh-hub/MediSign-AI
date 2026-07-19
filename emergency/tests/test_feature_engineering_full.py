"""Coverage tests for feature-engineering batch + report helpers (Phase 10)."""
from __future__ import annotations

import csv

import pytest

import utils.feature_utils as fu
from config.constants import HAND_LANDMARK_COUNT


def _write_landmarks_csv(path, n=21):
    cols = ["label", "video", "frame", "handedness", "score"] + [f"{ax}{i}" for i in range(n) for ax in ("x", "y", "z")]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        row = {c: "" for c in cols}
        row["label"] = "help"
        for i in range(n):
            row[f"x{i}"] = 0.1 * i
            row[f"y{i}"] = 0.2 * i
            row[f"z{i}"] = 0.0
        w.writerow(row)


def test_augment_landmark_rows():
    flat = [float(i) for i in range(63)]
    rows = [{"label": "help", "features": flat}]
    out, names = fu.augment_landmark_rows(rows)
    assert len(out) == 1
    assert len(out[0]["engineered"]) == len(names)
    assert len(names) == 210 + 14 + 5 + 2


def test_write_feature_report(tmp_path):
    summary = {
        "input_csv": "landmarks.csv",
        "output_csv": "features.csv",
        "rows": 1,
        "engineered_feature_count": 231,
        "total_feature_count": 294,
        "per_block": {"distances": 210, "angles": 14, "finger_states": 5, "palm_direction": 2},
    }
    md, js = fu.write_feature_report(summary, tmp_path)
    assert md.exists() and js.exists()
    assert "210" in md.read_text()


def test_run_feature_engineering_success(tmp_path):
    inp = tmp_path / "landmarks.csv"
    _write_landmarks_csv(inp, HAND_LANDMARK_COUNT)
    out = tmp_path / "features.csv"
    summary = fu.run_feature_engineering(input_csv=inp, output_csv=out, reports_dir=tmp_path)
    assert summary["skipped"] is False
    assert summary["rows"] == 1
    assert summary["total_feature_count"] == 294
    assert out.exists()
