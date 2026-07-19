"""Feature-engineering utilities (Phase 6).

Transforms the 21 normalised hand landmarks into a richer, more discriminative
feature vector: pairwise distances, joint angles, per-finger extension state, and
palm direction. Everything here is **pure Python** (no OpenCV/MediaPipe/numpy),
so it is fully unit-testable offline.

The default combined feature vector is the Phase-5 normalised coordinates (63
values) concatenated with the engineered features below. Each block is
config-gated via ``[features]`` so the representation is tunable.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import config
from config import PATHS
from config.constants import (
    ANGLE_TRIPLETS,
    FINGER_MCP_LANDMARKS,
    FINGER_PIP_LANDMARKS,
    FINGER_TIP_LANDMARKS,
    HAND_LANDMARK_COUNT,
    LANDMARK_PAIRS,
    WRIST_INDEX,
)
from utils.io_utils import ensure_dir
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------
def _sub(a: List[float], b: List[float]) -> List[float]:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _dist(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _angle_at(b: List[float], a: List[float], c: List[float]) -> float:
    """Interior angle (radians) at ``b`` between segments ``b->a`` and ``b->c``."""
    v1 = _sub(b, a)
    v2 = _sub(b, c)
    dot = sum(x * y for x, y in zip(v1, v2))
    n1 = _dist(b, a)
    n2 = _dist(b, c)
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    cos = max(-1.0, min(1.0, dot / (n1 * n2)))
    return math.acos(cos)


# ---------------------------------------------------------------------------
# Feature blocks
# ---------------------------------------------------------------------------
def pairwise_distances(xyz: List[List[float]]) -> List[float]:
    """Euclidean distance for every unordered landmark pair."""
    return [_dist(xyz[i], xyz[j]) for i, j in LANDMARK_PAIRS]


def joint_angles(xyz: List[List[float]]) -> List[float]:
    """Interior angle (radians) at the middle landmark of each triplet."""
    return [_angle_at(xyz[b], xyz[a], xyz[c]) for a, b, c in ANGLE_TRIPLETS]


def finger_states(xyz: List[List[float]]) -> List[float]:
    """Binary extension state per finger (1 = extended, 0 = curled).

    A finger is "extended" when its tip is farther from the wrist than its PIP
    joint — a rotation-invariant cue that works in normalised space.
    """
    wrist = xyz[WRIST_INDEX]
    states: List[float] = []
    for finger in ("thumb", "index", "middle", "ring", "pinky"):
        tip = xyz[FINGER_TIP_LANDMARKS[finger]]
        pip = xyz[FINGER_PIP_LANDMARKS[finger]]
        extended = _dist(tip, wrist) > _dist(pip, wrist)
        states.append(1.0 if extended else 0.0)
    return states


def palm_direction(xyz: List[List[float]]) -> List[float]:
    """2D (x, y) unit vector from wrist to middle-finger MCP = palm orientation."""
    wrist = xyz[WRIST_INDEX]
    middle_mcp = xyz[FINGER_MCP_LANDMARKS["middle"]]
    v = _sub(middle_mcp, wrist)
    norm = math.sqrt(v[0] ** 2 + v[1] ** 2)
    if norm == 0.0:
        return [0.0, 0.0]
    return [v[0] / norm, v[1] / norm]


# ---------------------------------------------------------------------------
# Naming + combination
# ---------------------------------------------------------------------------
def xyz_from_flat(flat: List[float]) -> List[List[float]]:
    """Convert a flat 63-value row back into 21 ``[x, y, z]`` landmarks."""
    return [[flat[i], flat[i + 1], flat[i + 2]] for i in range(0, len(flat), 3)]


def engineered_feature_names(flags: Optional[Dict] = None) -> List[str]:
    """Column names for the engineered blocks, in the order they are computed."""
    flags = flags if flags is not None else config.CONFIG["features"]
    names: List[str] = []
    if flags.get("compute_distances"):
        names.extend(f"dist_{i}_{j}" for i, j in LANDMARK_PAIRS)
    if flags.get("compute_angles"):
        names.extend(f"angle_{a}_{b}_{c}" for a, b, c in ANGLE_TRIPLETS)
    if flags.get("compute_finger_states"):
        names.extend(f"finger_{f}" for f in ("thumb", "index", "middle", "ring", "pinky"))
    if flags.get("compute_palm_direction"):
        names.extend(["palm_x", "palm_y"])
    return names


def compute_engineered_features(xyz: List[List[float]], flags: Optional[Dict] = None) -> List[float]:
    """Compute the engineered feature block(s) for one hand's landmarks."""
    flags = flags if flags is not None else config.CONFIG["features"]
    feats: List[float] = []
    if flags.get("compute_distances"):
        feats.extend(pairwise_distances(xyz))
    if flags.get("compute_angles"):
        feats.extend(joint_angles(xyz))
    if flags.get("compute_finger_states"):
        feats.extend(finger_states(xyz))
    if flags.get("compute_palm_direction"):
        feats.extend(palm_direction(xyz))
    return feats


def build_feature_vector(flat: List[float], flags: Optional[Dict] = None) -> List[float]:
    """Combine the normalised 63-value base with the engineered features."""
    xyz = xyz_from_flat(flat)
    return list(flat) + compute_engineered_features(xyz, flags)


def feature_column_names(flags: Optional[Dict] = None) -> List[str]:
    """Full column names for ``build_feature_vector`` output."""
    from config.constants import HAND_LANDMARK_COUNT

    base = [f"{ax}{i}" for i in range(HAND_LANDMARK_COUNT) for ax in ("x", "y", "z")]
    return base + engineered_feature_names(flags)


# ---------------------------------------------------------------------------
# Batch: read Phase-5 landmarks.csv -> features.csv + report
# ---------------------------------------------------------------------------
def augment_landmark_rows(rows: List[Dict[str, object]], flags: Optional[Dict] = None) -> Tuple[List[Dict[str, object]], List[str]]:
    """Add an ``engineered`` feature list to each landmark row."""
    flags = flags if flags is not None else config.CONFIG["features"]
    out: List[Dict[str, object]] = []
    for r in rows:
        flat = list(r.get("features", []))
        xyz = xyz_from_flat(flat)
        engineered = compute_engineered_features(xyz, flags)
        new_row = dict(r)
        new_row["engineered"] = engineered
        out.append(new_row)
    return out, engineered_feature_names(flags)


def write_features_csv(
    input_csv: str | Path,
    output_csv: str | Path,
    flags: Optional[Dict] = None,
) -> Dict[str, object]:
    """Read a Phase-5 landmarks CSV and write an augmented features CSV.

    Returns a dict with row count, engineered feature count, and paths.
    """
    input_csv = Path(input_csv)
    output_csv = Path(output_csv)
    ensure_dir(output_csv.parent)
    flags = flags if flags is not None else config.CONFIG["features"]
    eng_names = engineered_feature_names(flags)

    base_cols = ["label", "video", "frame", "handedness", "score"]
    base_coord_cols = [f"{ax}{i}" for i in range(HAND_LANDMARK_COUNT) for ax in ("x", "y", "z")]
    out_cols = base_cols + base_coord_cols + eng_names

    row_count = 0
    with input_csv.open(newline="", encoding="utf-8") as fin, output_csv.open("w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=out_cols)
        writer.writeheader()
        for raw in reader:
            flat = [float(raw[f"{ax}{i}"]) for i in range(HAND_LANDMARK_COUNT) for ax in ("x", "y", "z")]
            xyz = xyz_from_flat(flat)
            engineered = compute_engineered_features(xyz, flags)
            row = {k: raw.get(k, "") for k in base_cols}
            for i, ax in [(i, ax) for i in range(HAND_LANDMARK_COUNT) for ax in ("x", "y", "z")]:
                row[f"{ax}{i}"] = flat[i * 3 + {"x": 0, "y": 1, "z": 2}[ax]]
            for name, val in zip(eng_names, engineered):
                row[name] = val
            writer.writerow(row)
            row_count += 1

    result: Dict[str, object] = {
        "input_csv": str(input_csv),
        "output_csv": str(output_csv),
        "rows": row_count,
        "engineered_feature_count": len(eng_names),
        "total_feature_count": len(base_coord_cols) + len(eng_names),
    }
    return result


def write_feature_report(summary: Dict[str, object], reports_dir: str | Path) -> tuple[Path, Path]:
    """Write ``feature_report.md`` and ``feature_report.json``."""
    reports_dir = ensure_dir(reports_dir)
    md = reports_dir / "feature_report.md"
    js = reports_dir / "feature_report.json"
    counts = summary.get("per_block", {})
    lines = [
        "# Feature Engineering Report — Emergency Gesture Recognition",
        "",
        f"- **Input:** `{summary.get('input_csv')}`",
        f"- **Output:** `{summary.get('output_csv')}`",
        f"- **Rows:** {summary.get('rows')}",
        f"- **Engineered features:** {summary.get('engineered_feature_count')}",
        f"- **Total features per sample:** {summary.get('total_feature_count')}",
        "",
        "## Feature blocks",
        "",
        "| Block | Count |",
        "|-------|------:|",
    ]
    for block, n in counts.items():
        lines.append(f"| {block} | {n} |")
    lines.append("")
    md.write_text("\n".join(lines), encoding="utf-8")
    js.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote feature report -> %s and %s", md, js)
    return md, js


def run_feature_engineering(
    input_csv: Optional[str | Path] = None,
    output_csv: Optional[str | Path] = None,
    reports_dir: Optional[str | Path] = None,
    *,
    flags: Optional[Dict] = None,
    cfg: Optional[Dict] = None,
) -> Dict[str, object]:
    """End-to-end: read landmarks CSV, write features CSV, write report."""
    cfg = cfg or config.CONFIG
    flags = flags if flags is not None else cfg["features"]
    input_csv = Path(input_csv) if input_csv else PATHS["landmarks_dir"] / "landmarks.csv"
    output_csv = Path(output_csv) if output_csv else PATHS["landmarks_dir"] / "features.csv"
    rep_dir = Path(reports_dir) if reports_dir else PATHS["reports_dir"]
    eng_names = engineered_feature_names(flags)

    if not input_csv.exists():
        logger.warning("Landmarks CSV not found at %s (run Phase 5 first). Skipping feature engineering.", input_csv)
        return {
            "input_csv": str(input_csv),
            "output_csv": str(output_csv),
            "rows": 0,
            "engineered_feature_count": len(eng_names),
            "total_feature_count": HAND_LANDMARK_COUNT * 3 + len(eng_names),
            "skipped": True,
        }

    written = write_features_csv(input_csv, output_csv, flags)
    per_block = {
        "distances": len(LANDMARK_PAIRS) if flags.get("compute_distances") else 0,
        "angles": len(ANGLE_TRIPLETS) if flags.get("compute_angles") else 0,
        "finger_states": 5 if flags.get("compute_finger_states") else 0,
        "palm_direction": 2 if flags.get("compute_palm_direction") else 0,
    }
    summary = dict(written)
    summary["skipped"] = False
    summary["per_block"] = per_block
    write_feature_report(summary, rep_dir)
    logger.info("Feature engineering complete: %d rows, %d total features", summary["rows"], summary["total_feature_count"])
    return summary
