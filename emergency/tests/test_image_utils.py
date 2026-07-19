"""Tests for image-processing utilities (Phase 4).

Pure/planning/orchestration logic runs without OpenCV. Pixel-level transforms
are covered in ``test_image_processing_integration.py`` (skipped offline).
"""
from __future__ import annotations

import json
from pathlib import Path

import utils.image_utils as iu


# --------------------------------------------------------------------------
# Processing-plan construction (pure)
# --------------------------------------------------------------------------
def test_plan_default_includes_all():
    cfg = {
        "normalize": True,
        "contrast_clip_limit": 2.0,
        "histogram_equalization": True,
        "noise_reduction": True,
    }
    plan = iu.build_processing_plan(cfg)
    assert plan == ["resize", "contrast", "histogram_equalization", "noise_reduction", "normalize"]


def test_plan_resize_always_present():
    plan = iu.build_processing_plan({"normalize": False, "contrast_clip_limit": 0, "histogram_equalization": False, "noise_reduction": False})
    assert plan == ["resize"]


def test_plan_contrast_gated_by_clip_limit():
    plan = iu.build_processing_plan({"normalize": True, "contrast_clip_limit": 0.0, "histogram_equalization": True, "noise_reduction": False})
    assert "contrast" not in plan
    assert "histogram_equalization" in plan
    assert "normalize" in plan


# --------------------------------------------------------------------------
# Orchestration offline (cv2 absent -> every frame reported failed)
# --------------------------------------------------------------------------
def test_process_dataset_images_offline_manifest(tmp_path):
    # Build a fake frames tree.
    frames = tmp_path / "frames"
    f1 = frames / "help" / "help001_01" / "frame_00000.jpg"
    f2 = frames / "help" / "help001_01" / "frame_00001.jpg"
    f1.parent.mkdir(parents=True)
    f1.write_bytes(b"dummy")
    f2.write_bytes(b"dummy")

    manifest = iu.process_dataset_images(frames_dir=frames, out_dir=tmp_path / "processed", overwrite=True)
    assert manifest["summary"]["total_frames"] == 2
    # Without cv2 the frames cannot be decoded -> reported failed, not raised.
    assert manifest["summary"]["failed"] == 2
    assert len(manifest["failed_frames"]) == 2
    manifest_file = tmp_path / "processed" / "manifest.json"
    assert manifest_file.exists()
    loaded = json.loads(manifest_file.read_text())
    assert loaded["summary"]["total_frames"] == 2
    # Plan is recorded so downstream phases know what was supposed to run.
    assert "resize" in loaded["processing_plan"]
