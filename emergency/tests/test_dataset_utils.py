"""Tests for dataset analysis utilities (Phase 2).

Pure standard-library tests: they build a tiny fake dataset on disk and never
require OpenCV, so they run green even in a minimal environment.
"""
from __future__ import annotations

import json

import pytest

import utils.dataset_utils as du


def _make_fake_dataset(root: "Path", labels) -> None:  # type: ignore[name-defined]
    for label in labels:
        d = root / label
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{label}001.avi").write_bytes(b"x" * 100)
        (d / f"{label}002.AVI").write_bytes(b"y" * 200)  # uppercase extension
    (root / "readme.txt").write_text("ignore me")  # not a video


@pytest.fixture
def fake_report(tmp_path):
    _make_fake_dataset(tmp_path, ["help", "doctor"])
    return du.scan_videos(tmp_path, classes=["help", "doctor"], extensions=["avi"], probe_metadata=False)


def test_scan_counts_and_size(fake_report):
    assert fake_report["summary"]["total_videos"] == 4
    # 100+200 per class * 2 classes
    assert fake_report["summary"]["total_size_bytes"] == (100 + 200) * 2
    assert fake_report["summary"]["classes_count"] == 2
    assert fake_report["metadata_available"] is False


def test_case_insensitive_extensions(fake_report):
    exts = fake_report["per_class"]["help"]["extensions"]
    assert exts == {".avi": 2}
    assert ".AVI" not in exts  # normalised to lowercase


def test_non_video_files_ignored(fake_report):
    # the stray .txt must not be counted
    assert fake_report["summary"]["total_videos"] == 4


def test_missing_class_is_empty(tmp_path):
    report = du.scan_videos(tmp_path, classes=["help", "pain"], extensions=["avi"], probe_metadata=False)
    assert report["per_class"]["pain"]["video_count"] == 0
    assert report["per_class"]["help"]["video_count"] == 0


def test_metadata_unavailable_marks_note(tmp_path):
    # Note is emitted only when probing was attempted but OpenCV is missing.
    report = du.scan_videos(tmp_path, classes=["help"], extensions=["avi"], probe_metadata=True)
    assert any("OpenCV" in n for n in report["notes"])


def test_render_markdown(fake_report):
    md = du.render_markdown(fake_report)
    assert "Dataset Analysis Report" in md
    assert "| Class |" in md
    assert "help" in md and "doctor" in md


def test_write_reports(tmp_path):
    report = du.scan_videos(tmp_path, classes=["help"], extensions=["avi"], probe_metadata=False)
    (tmp_path / "help").mkdir()
    (tmp_path / "help" / "h.avi").write_bytes(b"z" * 50)
    report = du.scan_videos(tmp_path, classes=["help"], extensions=["avi"], probe_metadata=False)
    md_path, json_path = du.write_reports(report, tmp_path / "out")
    assert md_path.exists() and json_path.exists()
    loaded = json.loads(json_path.read_text())
    assert loaded["summary"]["total_videos"] == 1


def test_cv2_available_is_bool():
    assert isinstance(du._cv2_available(), bool)
