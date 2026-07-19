"""Tests for landmark extraction (Phase 5).

Pure logic — normalisation, CSV writing, reporting — runs without MediaPipe or
OpenCV. Actual detection is covered in ``test_landmark_extraction_integration.py``
(skipped when deps are absent).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from types import SimpleNamespace

import utils.landmark_utils as lu


# --------------------------------------------------------------------------
# Pure helpers
# --------------------------------------------------------------------------
def test_feature_columns():
    cols = lu.landmark_feature_columns()
    assert len(cols) == 63
    assert cols[0] == "x0" and cols[1] == "y0" and cols[2] == "z0"
    assert cols[-1] == "z20"


def test_landmark_obj_to_xyz():
    fake = [SimpleNamespace(x=0.1, y=0.2, z=0.3), SimpleNamespace(x=0.4, y=0.5, z=0.6)]
    xyz = lu.landmark_obj_to_xyz(fake)
    assert xyz == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


def test_normalize_wrist_centered():
    xyz = [[0.5, 0.5, 0.0]] + [[0.6, 0.6, 0.0], [0.4, 0.4, 0.0]]
    out = lu.normalize_landmarks(xyz, normalize=True)
    assert len(out) == 9
    # wrist maps to origin
    assert out[0] == 0.0 and out[1] == 0.0 and out[2] == 0.0


def test_normalize_scale_invariant():
    xyz = [[0.5, 0.5, 0.0], [0.6, 0.6, 0.0], [0.4, 0.4, 0.0]]
    a = lu.normalize_landmarks(xyz, normalize=True)
    scaled = [[v * 3 for v in p] for p in xyz]
    b = lu.normalize_landmarks(scaled, normalize=True)
    assert a == b  # scaling the whole hand does not change the normalised vector


def test_normalize_raw_returns_centered():
    xyz = [[0.5, 0.5, 0.0], [0.6, 0.6, 0.0], [0.4, 0.4, 0.0]]
    out = lu.normalize_landmarks(xyz, normalize=False)
    assert out[0] == 0.0
    assert out[3] == pytest.approx(0.1)
    assert out[6] == pytest.approx(-0.1)


def test_normalize_empty_returns_zeros():
    assert lu.normalize_landmarks([], normalize=True) == [0.0] * 63


# --------------------------------------------------------------------------
# CSV + report writing (stdlib; offline)
# --------------------------------------------------------------------------
def test_write_landmark_dataset_csv_and_headers(tmp_path):
    rows = [
        {"label": "help", "video": "help001_01", "frame": "frame_00000", "handedness": "Right", "score": 0.9, "features": [float(i) for i in range(63)]},
    ]
    csv_path = tmp_path / "landmarks.csv"
    written = lu.write_landmark_dataset(rows, csv_path, parquet_path=tmp_path / "landmarks.parquet")
    assert written["csv"] == str(csv_path)
    # Parquet is best-effort; offline it is skipped.
    assert written["parquet_written"] is False
    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames[0] == "label"
        assert reader.fieldnames[-1] == "z20"
        data = list(reader)
        assert len(data) == 1
        assert data[0]["label"] == "help"
        assert float(data[0]["x0"]) == 0.0
        assert float(data[0]["z20"]) == 62.0


def test_write_landmark_report(tmp_path):
    summary = {"total_frames": 10, "detected": 8, "no_hand": 1, "errors": 1, "parquet_written": False, "per_class": {"help": 8}}
    md, js = lu.write_landmark_report(summary, tmp_path)
    assert md.exists() and js.exists()
    loaded = json.loads(js.read_text())
    assert loaded["detected"] == 8
    assert "Detection rate" in md.read_text()


def test_extract_dataset_landmarks_offline(tmp_path):
    # Fake cleaned frames; MediaPipe/cv2 absent -> every frame is an error.
    frames = tmp_path / "processed" / "help" / "help001_01"
    frames.mkdir(parents=True)
    (frames / "frame_00000.jpg").write_bytes(b"dummy")
    (frames / "frame_00001.jpg").write_bytes(b"dummy")

    manifest = lu.extract_dataset_landmarks(
        frames_dir=tmp_path / "processed",
        out_dir=tmp_path / "landmarks",
        reports_dir=tmp_path / "reports",
        overwrite=True,
    )
    s = manifest["summary"]
    assert s["total_frames"] == 2
    assert s["detected"] == 0
    assert s["errors"] == 2  # hands model unavailable offline
    assert (tmp_path / "landmarks" / "landmarks.csv").exists()
    assert (tmp_path / "landmarks" / "manifest.json").exists()
    assert (tmp_path / "reports" / "landmark_report.json").exists()
    # CSV header-only when no detections
    with (tmp_path / "landmarks" / "landmarks.csv").open(newline="") as fh:
        assert len(list(csv.DictReader(fh))) == 0
