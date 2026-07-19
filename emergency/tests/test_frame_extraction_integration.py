"""Integration tests for frame extraction (Phase 3).

These require OpenCV (``cv2``) and NumPy. They are **skipped automatically** in
environments without those packages, so the offline suite stays green. When the
dependencies are installed (``pip install -r emergency/requirements.txt``) a
synthetic video is generated and the full extract → write → idempotent-resume
flow is exercised.
"""
from __future__ import annotations

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

import utils.video_utils as vu


def _make_synthetic_video(path: str, num_frames: int = 30, fps: int = 30, size=(64, 64)) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(path, fourcc, float(fps), size)
    if not writer.isOpened():
        pytest.skip("VideoWriter unavailable in this environment")
    for i in range(num_frames):
        frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        cv2.rectangle(frame, (i, i), (i + 10, i + 10), (255, 255, 255), -1)
        writer.write(frame)
    writer.release()


def test_extract_real_video_writes_frames(tmp_path):
    video = tmp_path / "clip.avi"
    _make_synthetic_video(str(video), num_frames=30, fps=30)
    out = tmp_path / "frames"
    summary = vu.extract_video_frames(video, out, label="help", fps_target=10, max_frames_per_video=60)
    assert summary["corrupted"] is False
    assert 1 <= summary["frames_written"] <= 60
    written_files = list((out / "help" / "clip").glob("*.jpg"))
    assert len(written_files) == summary["frames_written"]


def test_extraction_is_idempotent(tmp_path):
    video = tmp_path / "clip.avi"
    _make_synthetic_video(str(video), num_frames=30, fps=30)
    out = tmp_path / "frames"
    first = vu.extract_video_frames(video, out, label="help", fps_target=10, max_frames_per_video=60)
    second = vu.extract_video_frames(video, out, label="help", fps_target=10, max_frames_per_video=60, overwrite=False)
    assert second["skipped_existing"] is True
    assert second["frames_written"] == first["frames_written"]
