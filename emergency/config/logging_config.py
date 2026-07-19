"""Logging configuration helpers for the Emergency Gesture Recognition module.

Centralises formatter selection and handler construction so that both the
prediction engine and the batch scripts emit consistent, structured logs.
"""
from __future__ import annotations

import logging
from typing import Optional

from config import settings as _settings
from config.paths import PATHS

_TEXT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_JSON_FORMAT = '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'


def get_log_level() -> int:
    """Return the configured logging level as a ``logging`` constant."""
    raw = str(_settings.get_settings()["logging"].get("level", "INFO")).upper()
    return getattr(logging, raw, logging.INFO)


def get_formatter() -> logging.Formatter:
    """Return a log formatter based on the ``logging.format`` config value."""
    fmt_style = str(_settings.get_settings()["logging"].get("format", "text")).lower()
    pattern = _JSON_FORMAT if fmt_style == "json" else _TEXT_FORMAT
    return logging.Formatter(pattern, datefmt="%Y-%m-%dT%H:%M:%S")


def file_handler(name: str = "pipeline.log") -> Optional[logging.FileHandler]:
    """Create a rotating-free file handler under the configured logs directory.

    Returns ``None`` when file logging is disabled or the directory cannot be
    created, so callers can safely ignore it.
    """
    if not _settings.get_settings()["logging"].get("to_file", True):
        return None
    try:
        logs_dir = PATHS["logs_dir"]
        logs_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(logs_dir / name, encoding="utf-8")
        handler.setFormatter(get_formatter())
        return handler
    except OSError:
        return None
