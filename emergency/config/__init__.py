"""Configuration package for the MediSign-AI Emergency Gesture Recognition module.

Convenience re-exports so other modules can simply do::

    from config import CONFIG, PATHS, CONSTANTS

* ``CONFIG``    - the merged configuration mapping (defaults <- config.toml)
* ``PATHS``     - resolved :class:`~pathlib.Path` objects for every artifact dir
* ``CONSTANTS`` - structural constants (landmark indices, seed, counts, ...)

The loader module itself remains available as ``config.settings`` (call
``config.settings.get_settings()`` to re-read config programmatically).
"""
from .settings import get_settings
from .paths import resolve_paths, PATHS
from . import constants as CONSTANTS

# Materialise the merged settings mapping once at import time.
CONFIG: dict = get_settings()

__all__ = ["CONFIG", "PATHS", "CONSTANTS", "get_settings", "resolve_paths"]
