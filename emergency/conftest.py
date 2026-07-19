"""Pytest configuration for the Emergency Gesture Recognition module.

Ensures the ``emergency/`` directory is importable as a package root so that
tests can do ``import config``, ``import utils``, etc. without installing the
module.
"""
from __future__ import annotations

import sys
from pathlib import Path

EMERGENCY_ROOT = Path(__file__).resolve().parent
if str(EMERGENCY_ROOT) not in sys.path:
    sys.path.insert(0, str(EMERGENCY_ROOT))
