"""Structural constants for the Emergency Gesture Recognition module.

These are *structural* values that do not change between runs (MediaPipe hand
landmark topology, random seed defaults, version strings). Tunable runtime
parameters (class list, frame rate, model hyper-parameters, ...) live in
``config.toml`` and are accessed via :data:`config.settings`.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Project identity
# ---------------------------------------------------------------------------
PROJECT_NAME = "MediSign-AI Emergency Gesture Recognition"
DEFAULT_RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# MediaPipe Hands topology
# ---------------------------------------------------------------------------
#: Number of landmarks MediaPipe Hands returns per detected hand.
HAND_LANDMARK_COUNT = 21

#: Index of the wrist landmark (used as the origin for normalisation).
WRIST_INDEX = 0

#: Canonical MediaPipe hand-landmark names, indexed by landmark id.
HAND_LANDMARK_NAMES: tuple[str, ...] = (
    "wrist",
    "thumb_cmc", "thumb_mcp", "thumb_ip", "thumb_tip",
    "index_mcp", "index_pip", "index_dip", "index_tip",
    "middle_mcp", "middle_pip", "middle_dip", "middle_tip",
    "ring_mcp", "ring_pip", "ring_dip", "ring_tip",
    "pinky_mcp", "pinky_pip", "pinky_dip", "pinky_tip",
)

#: Tip landmark index for each of the five fingers.
FINGER_TIP_LANDMARKS: dict[str, int] = {
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20,
}

#: PIP (intermediate) joint index for each finger (used for finger-state logic).
FINGER_PIP_LANDMARKS: dict[str, int] = {
    "thumb": 3,
    "index": 6,
    "middle": 10,
    "ring": 14,
    "pinky": 18,
}

#: MCP (knuckle) joint index for each finger.
FINGER_MCP_LANDMARKS: dict[str, int] = {
    "thumb": 2,
    "index": 5,
    "middle": 9,
    "ring": 13,
    "pinky": 17,
}

#: Landmarks used to estimate palm direction / orientation.
PALM_VECTOR_LANDMARKS = (WRIST_INDEX, FINGER_MCP_LANDMARKS["middle"])

# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------
#: All unordered landmark pairs used for pairwise distance features.
def _pairwise_indices() -> list[tuple[int, int]]:
    idx = list(range(HAND_LANDMARK_COUNT))
    pairs: list[tuple[int, int]] = []
    for i in idx:
        for j in idx[i + 1:]:
            pairs.append((i, j))
    return pairs


LANDMARK_PAIRS: list[tuple[int, int]] = _pairwise_indices()

#: Adjacent landmark pairs used for angle (joint) features.
ANGLE_TRIPLETS: list[tuple[int, int, int]] = [
    (0, 5, 8),    # wrist -> index_mcp -> index_tip (index finger flex)
    (0, 9, 12),   # wrist -> middle_mcp -> middle_tip
    (0, 13, 16),  # wrist -> ring_mcp -> ring_tip
    (0, 17, 20),  # wrist -> pinky_mcp -> pinky_tip
    (1, 2, 3),    # thumb chain
    (2, 3, 4),    # thumb tip chain
    (5, 6, 7),    # index chain
    (6, 7, 8),    # index tip chain
    (9, 10, 11),  # middle chain
    (10, 11, 12), # middle tip chain
    (13, 14, 15), # ring chain
    (14, 15, 16), # ring tip chain
    (17, 18, 19), # pinky chain
    (18, 19, 20), # pinky tip chain
]

#: Number of raw coordinates per hand (x, y, z for 21 landmarks).
COORDS_PER_HAND = HAND_LANDMARK_COUNT * 3

# ---------------------------------------------------------------------------
# MediaPipe hand-label constants
# ---------------------------------------------------------------------------
HANDEDNESS_LEFT = "Left"
HANDEDNESS_RIGHT = "Right"

# ---------------------------------------------------------------------------
# Prediction engine
# ---------------------------------------------------------------------------
#: Below this confidence a prediction is treated as "uncertain".
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
#: Number of steady identical frames required to confirm an alarm (future use).
CONFIRMATION_WINDOW = 5
