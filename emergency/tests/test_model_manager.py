"""Tests for the ModelManager class (Phase 1)."""
from __future__ import annotations

from pathlib import Path
import pytest

from utils.model_manager import get_model_manager, reset_model_manager, ModelManager


def test_model_manager_singleton():
    reset_model_manager()
    a = get_model_manager()
    b = get_model_manager()
    assert a is b
    reset_model_manager()


def test_model_manager_metadata():
    reset_model_manager()
    manager = get_model_manager()
    metadata = manager.get_metadata()
    
    assert "version" in metadata
    assert "models" in metadata
    models = metadata["models"]
    
    assert "hand_landmarker" in models
    assert "sign_language" in models
    assert "emergency" in models
    assert "ocr" in models
    
    assert models["hand_landmarker"]["version"] == "0.10.10"
    assert models["sign_language"]["version"] == "1.0.0"
    assert models["emergency"]["version"] == "0.1.0"
    assert models["ocr"]["version"] == "0.1.0-MVP"


def test_model_manager_invalid_paths(monkeypatch):
    import utils.landmark_utils
    def mock_fail(p):
        raise Exception("mocked landmarker fail")
    monkeypatch.setattr(utils.landmark_utils, "create_hands", mock_fail)

    # Construct a custom manager with nonexistent paths
    custom_cfg = {
        "project": {"version": "0.9.9"},
        "training": {"model_filename": "nonexistent_emergency.pkl"},
        "api": {
            "sign_model_path": "nonexistent_sign.pkl",
            "hand_landmarker_task_path": "nonexistent_landmarker.task",
            "emergency_confidence_threshold": 0.8,
            "sign_confidence_threshold": 0.7
        },
        "landmarks": {
            "model_path": "nonexistent_landmarker.task",
            "max_num_hands": 1,
            "min_detection_confidence": 0.5
        }
    }
    manager = ModelManager(cfg=custom_cfg)
    
    assert manager.load_emergency_model() is False
    assert manager.load_sign_model() is False
    assert manager.load_landmarker() is False
