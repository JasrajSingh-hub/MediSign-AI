"""Structured logging setup for the Emergency Gesture Recognition module.

Provides :func:`get_logger`, a cached factory that attaches a console handler and
(optionally) a file handler exactly once per logger name, avoiding duplicate
log lines when modules are imported repeatedly.
"""
from __future__ import annotations

import logging

from config.logging_config import get_formatter, get_log_level, file_handler

#: Loggers already configured with handlers, so we never double-attach.
_CONFIGURED: set[str] = set()


def get_logger(name: str = "emergency", log_file: str = "pipeline.log") -> logging.Logger:
    """Return a configured logger.

    Parameters
    ----------
    name:
        Logger name (typically the module or script name).
    log_file:
        File name (under the configured logs directory) for the file handler.

    Returns
    -------
    logging.Logger
        A logger emitting to stdout and, when enabled, to a file.
    """
    logger = logging.getLogger(name)
    if name in _CONFIGURED:
        return logger

    logger.setLevel(get_log_level())
    formatter = get_formatter()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    fh = file_handler(log_file)
    if fh is not None:
        logger.addHandler(fh)

    # Do not propagate to the root logger (we manage our own handlers).
    logger.propagate = False
    _CONFIGURED.add(name)
    return logger


def reset_logger_registry() -> None:
    """Forget configured loggers (used by tests to avoid cross-test leakage)."""
    _CONFIGURED.clear()
