"""Tests for frame-extraction utilities (Phase 3).

Pure-logic tests (sampling math, path building, corrupted-skip, orchestration
manifest) run without OpenCV. Integration tests that need a real decoder live in
``test_frame_extraction_integration.py`` (skipped when cv2 is absent).
"""
from __future__ import annotations

from pathlib import Path

import pytest

import utils.video_utils as vu


# --------------------------------------------------------------------------
# Pure sampling logic
# --------------------------------------------------------------------------
def test_sample_known_fps_even():
    # 30 fps, target 10 fps -> interval 3 -> frames 0,3,6,... but capped at max
    idx = vu.sample_frame_indices(total_frames=100, video_fps=30, fps_target=10, max_frames_per_video=60)
    assert idx[0] == 0
    assert idx[1] == 3
    assert all(b - a == 3 for a, b in zip(idx, idx[1:]))


def test_sample_caps_at_max():
    idx = vu.sample_frame_indices(total_frames=1000, video_fps=30, fps_target=10, max_frames_per_video=60)
    assert len(idx) == 60
    assert idx[-1] <= 1000


def test_sample_unknown_fps_distributes_evenly():
    idx = vu.sample_frame_indices(total_frames=100, video_fps=0, fps_target=10, max_frames_per_video=10)
    assert len(idx) == 10
    # roughly evenly spread
    assert idx[0] == 0
    assert idx[-1] == 90


def test_sample_zero_frames_empty():
    assert vu.sample_frame_indices(0, 30, 10, 60) == []


def test_sample_small_video_keeps_all():
    idx = vu.sample_frame_indices(total_frames=5, video_fps=30, fps_target=10, max_frames_per_video=60)
    assert idx == [0, 1, 2, 3, 4]


# --------------------------------------------------------------------------
# Path building
# --------------------------------------------------------------------------
def test_build_frame_path():
    p = vu.build_frame_path("/out", "help", "help001_01", 7, "jpg")
    assert p == Path("/out/help/help001_01/frame_00007.jpg")


def test_build_frame_path_png_ext():
    p = vu.build_frame_path("/out", "pain", "x", 0, ".png")
    assert p.suffix == ".png"


# --------------------------------------------------------------------------
# Corrupted / missing video handling (works offline: cv2 import is caught)
# --------------------------------------------------------------------------
def test_extract_missing_video_marked_corrupted(tmp_path):
    summary = vu.extract_video_frames(tmp_path / "nope.avi", tmp_path / "frames", label="help")
    assert summary["corrupted"] is True
    assert summary["frames_written"] == 0
    # must not raise


# --------------------------------------------------------------------------
# Orchestration + manifest (offline: every video is "corrupted" w/o cv2)
# --------------------------------------------------------------------------
def test_extract_dataset_frames_writes_manifest(tmp_path):
    # Build a fake dataset with a couple of (non-video) .avi files per class.
    for label in ["help", "doctor"]:
        d = tmp_path / label
        d.mkdir()
        (d / f"{label}001.avi").write_bytes(b"dummy")
        (d / f"{label}002.avi").write_bytes(b"dummy")

    manifest = vu.extract_dataset_frames(
        root=tmp_path,
        out_dir=tmp_path / "frames",
        classes=["help", "doctor"],
        extensions=["avi"],
        overwrite=True,
    )
    assert manifest["summary"]["total_videos"] == 4
    # Without cv2 the videos are reported corrupted but the run must not raise.
    assert manifest["summary"]["corrupted"] == 4
    manifest_file = (tmp_path / "frames" / "manifest.json")
    assert manifest_file.exists()
    import json

    loaded = json.loads(manifest_file.read_text())
    assert loaded["summary"]["total_videos"] == 4
