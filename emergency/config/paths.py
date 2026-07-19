"""Filesystem path resolution for the Emergency Gesture Recognition module.

All paths are derived from the repository layout and the ``[paths]`` section of
``config.toml``. No absolute paths are hardcoded in source code; everything is
resolved relative to:

* :data:`REPO_ROOT`       - the MediSign-AI repository root (parent of ``emergency/``)
* :data:`EMERGENCY_ROOT`  - the ``emergency/`` module directory

``sos_dataset`` is resolved against the repository root because the raw videos
live at the repository root; every other artifact directory is resolved against
the emergency module directory.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import config.settings as _settings

#: Directory containing this module's parent package (``emergency/``).
EMERGENCY_ROOT = Path(__file__).resolve().parent.parent
#: Repository root (parent of ``emergency/``). Holds the raw ``SOS/`` videos.
REPO_ROOT = EMERGENCY_ROOT.parent

# Keys in ``[paths]`` that are resolved relative to the repository root instead
# of the emergency module directory.
_REPO_ROOT_KEYS = frozenset({"sos_dataset", "models_dir"})


def _resolve(value: str, base: Path) -> Path:
    """Resolve ``value`` against ``base`` unless it is already absolute."""
    candidate = Path(value)
    return candidate if candidate.is_absolute() else base / candidate


def resolve_paths(overrides: Optional[Dict[str, str]] = None) -> Dict[str, Path]:
    """Compute all artifact paths as :class:`~pathlib.Path` objects.

    Parameters
    ----------
    overrides:
        Optional mapping of ``[paths]`` keys to string values that take
        precedence over both the configuration file and the built-in defaults.
        Useful for tests and ephemeral runs.

    Returns
    -------
    dict[str, Path]
        Mapping of logical name -> resolved path.
    """
    cfg = dict(_settings.get_settings()["paths"])
    if overrides:
        cfg.update(overrides)

    paths: Dict[str, Path] = {
        "emergency_root": EMERGENCY_ROOT,
        "repo_root": REPO_ROOT,
        "sos_dataset": _resolve(cfg["sos_dataset"], REPO_ROOT),
        "frames_dir": _resolve(cfg["frames_dir"], EMERGENCY_ROOT),
        "processed_dir": _resolve(cfg["processed_dir"], EMERGENCY_ROOT),
        "landmarks_dir": _resolve(cfg["landmarks_dir"], EMERGENCY_ROOT),
        "models_dir": _resolve(cfg["models_dir"], REPO_ROOT),
        "reports_dir": _resolve(cfg["reports_dir"], EMERGENCY_ROOT),
        "logs_dir": _resolve(cfg["logs_dir"], EMERGENCY_ROOT),
        "dataset_artifacts_dir": _resolve(cfg["dataset_artifacts_dir"], EMERGENCY_ROOT),
    }
    return paths


#: Default resolved paths, computed once at import time.
PATHS: Dict[str, Path] = resolve_paths()
