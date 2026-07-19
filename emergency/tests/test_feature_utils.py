"""Tests for feature-engineering utilities (Phase 6).

Fully offline: all feature math is pure Python over the 21 normalised landmarks.
"""
from __future__ import annotations

import csv
import math
import tempfile
from pathlib import Path

import pytest

import utils.feature_utils as fu
from config.constants import LANDMARK_PAIRS, ANGLE_TRIPLETS, HAND_LANDMARK_COUNT


def _open_hand_xyz() -> list:
    """A synthetic open hand: wrist at origin, fingers extending +y."""
    wrist = [0.0, 0.0, 0.0]
    thumb = [[0.1, 0.05, 0], [0.2, 0.05, 0], [0.3, 0.05, 0], [0.4, 0.05, 0]]
    index = [[0.0, 0.15, 0], [0.0, 0.30, 0], [0.0, 0.45, 0], [0.0, 0.60, 0]]
    middle = [[0.0, 0.20, 0], [0.0, 0.35, 0], [0.0, 0.50, 0], [0.0, 0.65, 0]]
    ring = [[0.0, 0.15, 0], [0.0, 0.30, 0], [0.0, 0.45, 0], [0.0, 0.60, 0]]
    pinky = [[0.0, 0.10, 0], [0.0, 0.25, 0], [0.0, 0.40, 0], [0.0, 0.55, 0]]
    return [wrist] + thumb + index + middle + ring + pinky


def _curled_index(xyz):
    xyz = [list(p) for p in xyz]
    # move index tip (landmark 8) close to the wrist -> curled
    xyz[8] = [0.0, 0.10, 0]
    return xyz


# --------------------------------------------------------------------------
# Block sizes
# --------------------------------------------------------------------------
def test_pairwise_distance_count():
    assert len(fu.pairwise_distances(_open_hand_xyz())) == len(LANDMARK_PAIRS) == 210


def test_joint_angle_count():
    assert len(fu.joint_angles(_open_hand_xyz())) == len(ANGLE_TRIPLETS) == 14


def test_finger_states_open_hand_all_extended():
    states = fu.finger_states(_open_hand_xyz())
    assert states == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_finger_states_curl_flips_index():
    states = fu.finger_states(_curled_index(_open_hand_xyz()))
    assert states[1] == 0.0  # index curled
    assert states[0] == 1.0 and states[2] == 1.0


def test_palm_direction_upright():
    d = fu.palm_direction(_open_hand_xyz())
    assert len(d) == 2
    assert d[0] == pytest.approx(0.0, abs=1e-6)
    assert d[1] == pytest.approx(1.0, abs=1e-6)


def test_angles_in_range():
    for a in fu.joint_angles(_open_hand_xyz()):
        assert 0.0 <= a <= math.pi


# --------------------------------------------------------------------------
# Combination + naming
# --------------------------------------------------------------------------
def test_feature_column_names_total():
    names = fu.feature_column_names()
    assert len(names) == HAND_LANDMARK_COUNT * 3 + 210 + 14 + 5 + 2


def test_build_feature_vector_length_and_order():
    flat = [v for p in _open_hand_xyz() for v in p]
    vec = fu.build_feature_vector(flat)
    assert len(vec) == 294
    # engineered block begins right after the 63 base coords
    assert vec[63] == pytest.approx(fu.pairwise_distances(_open_hand_xyz())[0])


# --------------------------------------------------------------------------
# Batch CSV plumbing
# --------------------------------------------------------------------------
def _write_landmarks_csv(path: Path, xyz) -> None:
    flat = [v for p in xyz for v in p]
    cols = ["label", "video", "frame", "handedness", "score"] + [f"{ax}{i}" for i in range(21) for ax in ("x", "y", "z")]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        row = {"label": "help", "video": "v1", "frame": "f0", "handedness": "Right", "score": 1.0}
        for i, ax in [(i, ax) for i in range(21) for ax in ("x", "y", "z")]:
            row[f"{ax}{i}"] = flat[i * 3 + {"x": 0, "y": 1, "z": 2}[ax]]
        w.writerow(row)


def test_write_features_csv(tmp_path):
    inp = tmp_path / "landmarks.csv"
    _write_landmarks_csv(inp, _open_hand_xyz())
    out = tmp_path / "features.csv"
    res = fu.write_features_csv(inp, out)
    assert res["rows"] == 1
    assert res["total_feature_count"] == 294
    with out.open(newline="") as fh:
        reader = csv.DictReader(fh)
        assert "palm_x" in reader.fieldnames and "palm_y" in reader.fieldnames
        assert "dist_0_1" in reader.fieldnames
        row = next(reader)
        assert row["label"] == "help"
        assert float(row["palm_y"]) == pytest.approx(1.0, abs=1e-6)
        assert float(row["finger_index"]) == 1.0


def test_run_feature_engineering_missing_input_is_safe(tmp_path):
    # No landmarks.csv -> graceful skip, no raise.
    out = tmp_path / "features.csv"
    summary = fu.run_feature_engineering(input_csv=tmp_path / "landmarks.csv", output_csv=out, reports_dir=tmp_path)
    assert summary["skipped"] is True
    assert summary["rows"] == 0
