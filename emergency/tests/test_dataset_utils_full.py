"""Coverage tests for dataset analysis utilities (Phase 10 backfill)."""
from __future__ import annotations

import csv

import numpy as np
import pytest

import utils.dataset_utils as du


def _report(metadata_available=False, corrupted_videos=None):
    corrupted_videos = corrupted_videos or []
    return {
        "module": "M",
        "dataset_root": "/x",
        "classes": ["help"],
        "video_extensions": ["avi"],
        "metadata_available": metadata_available,
        "summary": {"total_videos": 1, "total_size_bytes": 1024, "classes_count": 1, "corrupted_count": len(corrupted_videos)},
        "per_class": {"help": {"video_count": 1, "total_size_bytes": 1024, "extensions": {".avi": 1}, "videos": corrupted_videos}},
        "notes": ["note-1"],
    }


def test_format_size():
    assert du._format_size(500) == "500.0 B"
    assert du._format_size(1024) == "1.0 KB"
    assert du._format_size(1024 * 1024 * 2) == "2.0 MB"


def test_render_markdown_no_metadata():
    md = du.render_markdown(_report(metadata_available=False))
    assert "Dataset Analysis Report" in md
    assert "| help |" in md
    assert "note-1" in md
    assert "no (OpenCV not installed)" in md


def test_render_markdown_with_metadata():
    md = du.render_markdown(_report(metadata_available=True, corrupted_videos=[{"corrupted": True}]))
    assert "Corrupted" in md


def test_write_reports(tmp_path):
    md, js = du.write_reports(_report(), tmp_path)
    assert md.exists() and js.exists()


def test_analyze_writes_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(du, "scan_videos", lambda *a, **k: _report())
    monkeypatch.setattr(du, "write_reports", lambda r, d: (tmp_path / "x.md", tmp_path / "x.json"))
    rep = du.analyze(report_dir=tmp_path)
    assert "summary" in rep


def test_probe_video_real(tmp_path):
    import cv2

    p = tmp_path / "v.avi"
    vw = cv2.VideoWriter(str(p), cv2.VideoWriter_fourcc(*"MJPG"), 5, (32, 32))
    for _ in range(5):
        vw.write(np.zeros((32, 32, 3), dtype=np.uint8))
    vw.release()
    rec = du._probe_video(p)
    assert rec["frame_count"] == 5
    assert rec["corrupted"] is False


def test_scan_videos_with_metadata(tmp_path):
    import cv2

    cls = tmp_path / "help"
    cls.mkdir()
    p = cls / "help001.avi"
    vw = cv2.VideoWriter(str(p), cv2.VideoWriter_fourcc(*"MJPG"), 5, (32, 32))
    for _ in range(4):
        vw.write(np.zeros((32, 32, 3), dtype=np.uint8))
    vw.release()

    report = du.scan_videos(tmp_path, classes=["help"], extensions=["avi"], probe_metadata=True)
    assert report["metadata_available"] is True
    assert report["summary"]["total_videos"] == 1
    assert report["summary"]["corrupted_count"] == 0


def test_scan_videos_corrupted(tmp_path):
    cls = tmp_path / "help"
    cls.mkdir()
    (cls / "bad.avi").write_bytes(b"not-a-video")
    report = du.scan_videos(tmp_path, classes=["help"], extensions=["avi"], probe_metadata=True)
    assert report["summary"]["total_videos"] == 1
    assert report["summary"]["corrupted_count"] == 1
