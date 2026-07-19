"""Integration tests for image processing (Phase 4).

Require OpenCV (``cv2``) and NumPy. Skipped automatically when absent. When the
dependencies are installed, a synthetic frame is written and the full
clean -> write flow plus each individual transform is verified.
"""
from __future__ import annotations

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

import utils.image_utils as iu


def _make_dummy_frame(path: str, size=(64, 64)) -> None:
    img = np.random.randint(0, 255, (size[1], size[0], 3), dtype=np.uint8)
    cv2.imwrite(path, img)


def test_each_transform_returns_uint8():
    img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    params = {"target_size": [48, 48], "contrast_clip_limit": 2.0, "denoise_strength": 7}
    for name in ["resize", "contrast", "histogram_equalization", "noise_reduction", "normalize"]:
        out = iu._TRANSFORMS[name](img, params)
        assert out.dtype == np.uint8, name
    # resize changes spatial size
    assert iu.resize_image(img, params).shape[:2] == (48, 48)


def test_process_dataset_images_writes_clean_frames(tmp_path):
    frames = tmp_path / "frames" / "help" / "help001_01"
    frames.mkdir(parents=True)
    _make_dummy_frame(str(frames / "frame_00000.jpg"))
    _make_dummy_frame(str(frames / "frame_00001.jpg"))

    manifest = iu.process_dataset_images(frames_dir=tmp_path / "frames", out_dir=tmp_path / "processed", overwrite=True)
    assert manifest["summary"]["processed"] == 2
    assert manifest["summary"]["failed"] == 0
    out_files = list((tmp_path / "processed").rglob("*.jpg"))
    assert len(out_files) == 2
    # Output matches the configured target size and is uint8 BGR.
    out_img = cv2.imread(str(out_files[0]))
    assert out_img is not None
    assert out_img.dtype == np.uint8
    assert out_img.shape[:2] == (256, 256)
