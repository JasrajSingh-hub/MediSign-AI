"""Central configuration loader for the Emergency Gesture Recognition module.

Reads ``config.toml`` and merges it over built-in default values. The TOML file
is parsed with the standard-library :mod:`tomllib` module so **no third-party
dependency** is required to load configuration (important for offline / CI
environments). The result is a plain nested ``dict`` and is cached for the
lifetime of the process.
"""
from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent / "config.toml"

# Built-in defaults. Used whenever a key is omitted from config.toml. Keeping the
# defaults here guarantees the module still boots with a minimal/empty config.
_DEFAULTS: dict[str, Any] = {
    "project": {"name": "MediSign-AI Emergency Gesture Recognition", "version": "0.1.0", "module_key": "emergency"},
    "paths": {
        "sos_dataset": "SOS",
        "frames_dir": "output/frames",
        "processed_dir": "output/processed",
        "landmarks_dir": "output/landmarks",
        "models_dir": "backend/models",
        "reports_dir": "reports",
        "logs_dir": "logs",
        "dataset_artifacts_dir": "dataset",
    },
    "dataset": {
        "classes": ["help", "doctor", "pain", "call", "accident", "hot"],
        "video_extensions": ["avi"],
        "train_test_split": 0.8,
        "random_seed": 42,
        "stratify": True,
    },
    "frame_extraction": {
        "fps_target": 10,
        "max_frames_per_video": 60,
        "skip_corrupted": True,
    },
    "image_processing": {
        "target_size": [256, 256],
        "normalize": True,
        "contrast_clip_limit": 2.0,
        "histogram_equalization": True,
        "noise_reduction": True,
        "denoise_strength": 7,
    },
    "landmarks": {
        "model_complexity": 1,
        "static_image_mode": True,
        "max_num_hands": 1,
        "min_detection_confidence": 0.5,
        "normalize_landmarks": True,
    },
    "features": {
        "compute_distances": True,
        "compute_angles": True,
        "compute_finger_states": True,
        "compute_palm_direction": True,
    },
    "training": {
        "algorithm": "random_forest",
        "n_estimators": 200,
        "max_depth": 20,
        "min_samples_leaf": 2,
        "n_splits_cv": 5,
        "grid_search": False,
        "model_filename": "emergency_model.pkl",
    },
    "api": {"host": "0.0.0.0", "port": 8000, "reload": False},
    "logging": {"level": "INFO", "format": "text", "to_file": True},
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into a copy of ``base``.

    Mapping values are merged key-by-key; every other value type in ``override``
    replaces the corresponding value in ``base``.
    """
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_dotenv() -> dict[str, str]:
    """Parse the centralized .env file at the repository root if present."""
    import os
    env_vars = {}
    # Repository root is parent of emergency module, settings is at emergency/config/settings.py
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.is_file():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    # Resolve quotes
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    elif val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    env_vars[key] = val
                    os.environ[key] = val
        except Exception as exc:
            print(f"Error loading .env file: {exc}")
    return env_vars


@lru_cache(maxsize=1)
def get_settings() -> dict[str, Any]:
    """Load and cache the merged configuration mapping.

    Returns
    -------
    dict
        Nested configuration with built-in defaults overridden by ``config.toml`` and ``.env``.
    """
    settings: dict[str, Any] = _DEFAULTS
    if CONFIG_PATH.is_file():
        with CONFIG_PATH.open("rb") as fh:
            file_settings = tomllib.load(fh)
        settings = _deep_merge(_DEFAULTS, file_settings)
    
    # Merge .env overrides
    env = _load_dotenv()
    if "MEDISIGN_HOST" in env:
        settings["api"]["host"] = env["MEDISIGN_HOST"]
    if "MEDISIGN_PORT" in env:
        settings["api"]["port"] = int(env["MEDISIGN_PORT"])
    if "MEDISIGN_LOG_LEVEL" in env:
        settings["logging"]["level"] = env["MEDISIGN_LOG_LEVEL"]
    
    # Model path overrides
    if "EMERGENCY_MODEL_PATH" in env:
        settings["training"]["model_filename"] = env["EMERGENCY_MODEL_PATH"]
    
    # Add new unified configurations
    settings["api"]["sign_model_path"] = env.get(
        "SIGN_MODEL_PATH", "../backend/models/gesture_model_full.pkl"
    )
    settings["api"]["hand_landmarker_task_path"] = env.get(
        "HAND_LANDMARKER_TASK_PATH", "models/hand_landmarker.task"
    )
    settings["api"]["emergency_confidence_threshold"] = float(
        env.get("EMERGENCY_CONFIDENCE_THRESHOLD", 0.80)
    )
    settings["api"]["sign_confidence_threshold"] = float(
        env.get("SIGN_CONFIDENCE_THRESHOLD", 0.70)
    )
    
    return settings


def reset_settings_cache() -> None:
    """Clear the cached settings (primarily for tests with alternate configs)."""
    get_settings.cache_clear()
