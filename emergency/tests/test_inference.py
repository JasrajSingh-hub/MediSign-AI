"""Tests for the image->prediction inference pipeline (Phase 9).

Offline: the missing-OpenCV path is exercised and must return a clear
``available=False`` result. The full pipeline is covered by
``test_api_integration.py`` once OpenCV/MediaPipe are installed.
"""
from __future__ import annotations

import utils.inference as inf


def test_predict_offline_returns_unavailable():
    res = inf.predict_from_image_bytes(b"not-an-image")
    assert res["available"] is False
    assert "cv2" in res["error"].lower() or "opencv" in res["error"].lower() or "decode" in res["error"].lower()


def test_predict_empty_bytes_unavailable():
    res = inf.predict_from_image_bytes(b"")
    assert res["available"] is False
