"""Unit tests for the pure config/utils modules (Phase 10 coverage backfill).

Exercises the offline-runnable core so the suite covers as much as possible
without OpenCV/MediaPipe/scikit-learn/FastAPI.
"""
from __future__ import annotations

import logging
from pathlib import Path

import config.settings as cs
import config.logging_config as lc
from config import PATHS
from config import constants as C
from config import paths as P
from utils import io_utils as iu
from utils import progress as pg


# --------------------------------------------------------------------------
# config.paths
# --------------------------------------------------------------------------
def test_paths_roots_exist():
    assert P.EMERGENCY_ROOT.exists()
    assert P.REPO_ROOT.exists()


def test_resolve_paths_override_relative():
    resolved = P.resolve_paths(overrides={"frames_dir": "x/y"})
    assert resolved["frames_dir"] == P.EMERGENCY_ROOT / "x/y"


def test_resolve_paths_override_absolute():
    abs_dir = Path.cwd() / "some_absolute_dir"
    resolved = P.resolve_paths(overrides={"sos_dataset": str(abs_dir)})
    assert resolved["sos_dataset"] == abs_dir


def test_resolve_paths_defaults_point_inside_module():
    assert PATHS["frames_dir"].is_relative_to(P.EMERGENCY_ROOT)


# --------------------------------------------------------------------------
# config.settings
# --------------------------------------------------------------------------
def test_get_settings_cached():
    a = cs.get_settings()
    b = cs.get_settings()
    assert a is b


def test_get_settings_structure():
    s = cs.get_settings()
    assert "dataset" in s and "classes" in s["dataset"]
    assert "hot" in s["dataset"]["classes"]


def test_settings_cache_reset_changes_object():
    first = cs.get_settings()
    cs.reset_settings_cache()
    second = cs.get_settings()
    assert first is not second
    cs.reset_settings_cache()


# --------------------------------------------------------------------------
# config.logging_config
# --------------------------------------------------------------------------
def test_log_level_is_int():
    assert isinstance(lc.get_log_level(), int)


def test_formatter_is_formatter():
    assert isinstance(lc.get_formatter(), logging.Formatter)


def test_file_handler_returns_handler_when_enabled():
    h = lc.file_handler("phase10_test.log")
    assert isinstance(h, logging.FileHandler)
    try:
        h.close()
    except Exception:
        pass


# --------------------------------------------------------------------------
# config.constants
# --------------------------------------------------------------------------
def test_constants_topology():
    assert C.HAND_LANDMARK_COUNT == 21
    assert len(C.LANDMARK_PAIRS) == 210
    assert len(C.ANGLE_TRIPLETS) == 14
    assert C.FINGER_TIP_LANDMARKS["index"] == 8
    assert C.WRIST_INDEX == 0


# --------------------------------------------------------------------------
# utils.io_utils
# --------------------------------------------------------------------------
def test_ensure_dir_returns_path_and_creates(tmp_path):
    d = iu.ensure_dir(tmp_path / "a" / "b")
    assert isinstance(d, Path) and d.exists()


def test_read_video_paths_case_insensitive(tmp_path):
    (tmp_path / "x.avi").write_bytes(b"1")
    (tmp_path / "y.AVI").write_bytes(b"2")
    (tmp_path / "z.txt").write_text("skip")
    found = iu.read_video_paths(tmp_path)
    assert len(found) == 2


def test_read_class_directories_handles_missing(tmp_path):
    (tmp_path / "help").mkdir(parents=True)
    (tmp_path / "help" / "a.avi").write_bytes(b"1")
    res = iu.read_class_directories(tmp_path, ["help", "doctor"])
    assert len(res["help"]) == 1
    assert res["doctor"] == []


def test_safe_filename_sanitizes():
    cleaned = iu.safe_filename("a/b:c*?d")
    assert "/" not in cleaned and ":" not in cleaned and "*" not in cleaned


# --------------------------------------------------------------------------
# utils.progress (no-op fallback when tqdm absent)
# --------------------------------------------------------------------------
def test_tqdm_yields_all_items():
    assert list(pg.tqdm([1, 2, 3])) == [1, 2, 3]


def test_tqdm_has_flag_is_bool():
    assert isinstance(pg._HAS_TQDM, bool)
