"""Hand-landmark extraction utilities (Phase 5).

Runs MediaPipe Hands to detect 21 landmarks per hand, normalises them
(wrist-centred + scale-invariant), and persists the result as CSV (stdlib,
always available) and Parquet (best-effort; skipped with a note when
``pyarrow``/``pandas`` are absent). MediaPipe and Parquet I/O are imported
**lazily** so the pure logic (normalisation, CSV writing, reporting) is
unit-testable without those heavy dependencies.

Per-frame rows contain only frames where a hand was actually detected; frames
without a hand are recorded in the manifest (not in the training CSV) so the
dataset is not polluted with all-zero rows.
"""
from __future__ import annotations

import csv
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

import config
from config import PATHS
from config.constants import HAND_LANDMARK_COUNT
from utils.io_utils import ensure_dir
from utils.logger import get_logger
from utils.progress import tqdm

logger = get_logger(__name__)


#: MediaPipe hand-landmark model (Tasks API). Auto-downloaded on first use if
#: it is missing, so the module works out-of-the-box without committing the
#: binary. The legacy ``mp.solutions.hands`` API was removed in MediaPipe
#: 0.10.10+, so the Tasks API (``mp.tasks.vision.HandLandmarker``) is used.
HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
DEFAULT_HAND_MODEL_NAME = "hand_landmarker.task"


# ---------------------------------------------------------------------------
# Pure helpers (no OpenCV / MediaPipe required)
# ---------------------------------------------------------------------------
def landmark_feature_columns(n: int = HAND_LANDMARK_COUNT) -> List[str]:
    """Return the 3*N flattened coordinate column names ``x0,y0,z0,...,z(N-1)``."""
    cols: List[str] = []
    for i in range(n):
        cols.extend([f"x{i}", f"y{i}", f"z{i}"])
    return cols


def landmark_obj_to_xyz(landmarks) -> List[List[float]]:
    """Convert MediaPipe landmark objects (``.x/.y/.z``) to a list of [x,y,z]."""
    return [[float(lm.x), float(lm.y), float(lm.z)] for lm in landmarks]


def normalize_landmarks(xyz: List[List[float]], normalize: bool = True) -> List[float]:
    """Wrist-centre and scale-normalise hand landmarks into a flat feature row.

    Parameters
    ----------
    xyz: entries of ``[x, y, z]`` (MediaPipe relative coordinates, 0..1). The
        Emergency module always passes 21 landmarks, yielding 63 values, but any
        count is accepted.
    normalize: When ``True`` (default) also scale by the hand bounding-box so the
        vector is invariant to hand distance from the camera.

    Returns
    -------
    list[float]
        Flat ``[x0,y0,z0, x1,y1,z1, ...]``. All-zero vector if ``xyz`` is empty.
    """
    if not xyz:
        return [0.0] * (HAND_LANDMARK_COUNT * 3)
    wrist = xyz[0]
    centred = [[p[0] - wrist[0], p[1] - wrist[1], p[2] - wrist[2]] for p in xyz]
    if not normalize:
        return [v for point in centred for v in point]
    xs = [p[0] for p in centred]
    ys = [p[1] for p in centred]
    scale = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    norm = [[p[0] / scale, p[1] / scale, p[2] / scale] for p in centred]
    return [v for point in norm for v in point]


# ---------------------------------------------------------------------------
# MediaPipe detection (lazy)
# ---------------------------------------------------------------------------
def _ensure_hand_model(model_path: Path) -> Path:
    """Return ``model_path``, downloading the MediaPipe model if it is absent."""
    model_path = Path(model_path)
    if model_path.exists():
        return model_path
    ensure_dir(model_path.parent)
    logger.info("Downloading MediaPipe hand model -> %s", model_path)
    urllib.request.urlretrieve(HAND_LANDMARKER_MODEL_URL, model_path)
    logger.info("Downloaded hand model (%d bytes)", model_path.stat().st_size)
    return model_path


def create_hands(params: Dict) -> "object":
    """Create and return a MediaPipe ``HandLandmarker`` (Tasks API, lazy import).

    The model asset (``hand_landmarker.task``) is resolved from ``params`` or,
    by default, from ``models_dir``; it is downloaded automatically on first use
    if missing.
    """
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    model_path = Path(params.get("model_path") or (PATHS["models_dir"] / DEFAULT_HAND_MODEL_NAME))
    model_path = _ensure_hand_model(model_path)

    base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=int(params.get("max_num_hands", 1)),
        min_hand_detection_confidence=float(params.get("min_detection_confidence", 0.5)),
        min_hand_presence_confidence=float(params.get("min_detection_confidence", 0.5)),
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


def detect_landmarks(image, hands) -> List[Dict[str, object]]:
    """Run a MediaPipe ``HandLandmarker`` on a BGR image and return detected hands.

    Each dict has ``handedness``, ``score``, and ``xyz`` (21×[x,y,z]).
    Returns an empty list when no hand is present.
    """
    import cv2
    import mediapipe as mp

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = hands.detect(mp_image)
    detections: List[Dict[str, object]] = []
    hand_landmarks_list = result.hand_landmarks or []
    handedness_list = result.handedness or []
    for lm, handed in zip(hand_landmarks_list, handedness_list):
        xyz = landmark_obj_to_xyz(lm)
        score = 0.0
        handed_label = ""
        if handed:
            score = float(handed[0].score)
            handed_label = handed[0].category_name
        detections.append({"handedness": handed_label, "score": score, "xyz": xyz})
    return detections


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def write_landmark_dataset(
    rows: List[Dict[str, object]],
    csv_path: str | Path,
    parquet_path: Optional[str | Path] = None,
) -> Dict[str, object]:
    """Write landmark rows to CSV (stdlib) and, best-effort, to Parquet.

    Returns a dict noting which artefacts were written.
    """
    csv_path = Path(csv_path)
    ensure_dir(csv_path.parent)
    cols = ["label", "video", "frame", "handedness", "score"] + landmark_feature_columns()
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            row = {
                "label": r.get("label", ""),
                "video": r.get("video", ""),
                "frame": r.get("frame", ""),
                "handedness": r.get("handedness", ""),
                "score": r.get("score", 0.0),
            }
            for col, val in zip(landmark_feature_columns(), r.get("features", [])):
                row[col] = val
            writer.writerow(row)

    result: Dict[str, object] = {"csv": str(csv_path), "parquet": None, "parquet_written": False}
    if parquet_path is not None:
        parquet_path = Path(parquet_path)
        try:
            import pandas as pd

            df = pd.DataFrame(
                [
                    {
                        **{
                            "label": r.get("label", ""),
                            "video": r.get("video", ""),
                            "frame": r.get("frame", ""),
                            "handedness": r.get("handedness", ""),
                            "score": r.get("score", 0.0),
                        },
                        **dict(zip(landmark_feature_columns(), r.get("features", []))),
                    }
                    for r in rows
                ]
            )
            ensure_dir(parquet_path.parent)
            df.to_parquet(parquet_path, index=False)
            result["parquet"] = str(parquet_path)
            result["parquet_written"] = True
        except ImportError:
            logger.info("Parquet skipped: pandas/pyarrow not installed (CSV is authoritative).")
    return result


def write_landmark_report(summary: Dict[str, object], reports_dir: str | Path) -> tuple[Path, Path]:
    """Write ``landmark_report.md`` and ``landmark_report.json``.

    ``summary`` must contain ``total_frames``, ``detected``, ``no_hand``,
    ``errors``, ``parquet_written``, and ``per_class`` (mapping label->detected).
    """
    reports_dir = ensure_dir(reports_dir)
    md_path = reports_dir / "landmark_report.md"
    json_path = reports_dir / "landmark_report.json"

    total = int(summary.get("total_frames", 0)) or 1
    detected = int(summary.get("detected", 0))
    rate = detected / total if total else 0.0
    lines = [
        "# Landmark Extraction Report — Emergency Gesture Recognition",
        "",
        f"- **Total frames:** {total}",
        f"- **Frames with a detected hand:** {detected}",
        f"- **Detection rate:** {rate:.1%}",
        f"- **Frames without a hand:** {summary.get('no_hand', 0)}",
        f"- **Errors:** {summary.get('errors', 0)}",
        f"- **Parquet written:** {bool(summary.get('parquet_written'))}",
        "",
        "## Per-class detection",
        "",
        "| Class | Detected frames |",
        "|-------|----------------:|",
    ]
    for label, count in summary.get("per_class", {}).items():
        lines.append(f"| {label} | {count} |")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    json_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote landmark report -> %s and %s", md_path, json_path)
    return md_path, json_path


# ---------------------------------------------------------------------------
# Batch extraction
# ---------------------------------------------------------------------------
def extract_dataset_landmarks(
    frames_dir: Optional[str | Path] = None,
    out_dir: Optional[str | Path] = None,
    reports_dir: Optional[str | Path] = None,
    *,
    overwrite: bool = False,
    progress: bool = True,
    cfg: Optional[Dict] = None,
) -> Dict[str, object]:
    """Extract landmarks from every cleaned frame and persist CSV/Parquet/report.

    Returns a manifest dict. When MediaPipe/cv2 are unavailable every frame is
    recorded as an error (not raised) so the batch still completes.
    """
    cfg = cfg or config.CONFIG
    frames_root = Path(frames_dir) if frames_dir else PATHS["processed_dir"]
    out_root = Path(out_dir) if out_dir else PATHS["landmarks_dir"]
    rep_dir = Path(reports_dir) if reports_dir else PATHS["reports_dir"]
    lm_cfg = cfg["landmarks"]
    normalize = bool(lm_cfg.get("normalize_landmarks", True))

    frame_files: List[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        frame_files.extend(frames_root.rglob(ext))
    frame_files = sorted(frame_files)

    rows: List[Dict[str, object]] = []
    per_class: Dict[str, int] = {}
    detected = 0
    no_hand = 0
    errors = 0

    # Build the MediaPipe model once (or None if unavailable).
    hands = None
    try:
        hands = create_hands(lm_cfg)
    except Exception as exc:
        logger.warning("Hand model unavailable; landmark extraction will record 0 detections: %s", exc)

    iterator: List[Path] = frame_files
    if progress:
        iterator = tqdm(frame_files, desc="Extracting landmarks", unit="frame")

    for src in iterator:
        try:
            rel = src.relative_to(frames_root)
        except ValueError:
            rel = Path(src.name)
        parts = rel.parts
        label = parts[0] if len(parts) > 1 else ""
        video = parts[1] if len(parts) > 2 else rel.stem
        frame = rel.stem

        if hands is None:
            errors += 1
            continue
        try:
            import cv2

            img = cv2.imread(str(src))
            if img is None:
                errors += 1
                continue
            detections = detect_landmarks(img, hands)
            if not detections:
                no_hand += 1
                continue
            primary = detections[0]
            features = normalize_landmarks(primary["xyz"], normalize=normalize)
            rows.append(
                {
                    "label": label,
                    "video": video,
                    "frame": frame,
                    "handedness": primary["handedness"],
                    "score": primary["score"],
                    "features": features,
                }
            )
            detected += 1
            per_class[label] = per_class.get(label, 0) + 1
        except Exception as exc:  # pragma: no cover - defensive
            errors += 1
            logger.warning("Failed landmark extraction for %s: %s", src, exc)

    if hands is not None:
        try:
            hands.close()
        except Exception:  # pragma: no cover
            pass

    summary = {
        "total_frames": len(frame_files),
        "detected": detected,
        "no_hand": no_hand,
        "errors": errors,
        "per_class": per_class,
    }
    ensure_dir(out_root)
    csv_path = out_root / "landmarks.csv"
    parquet_path = out_root / "landmarks.parquet"
    written = write_landmark_dataset(rows, csv_path, parquet_path)
    summary["parquet_written"] = written["parquet_written"]
    summary["csv_path"] = written["csv"]
    summary["parquet_path"] = written["parquet"]

    manifest = {"summary": summary, "rows": len(rows), "landmarks_dir": str(out_root)}
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    summary_for_report = dict(summary)
    summary_for_report["parquet_written"] = written["parquet_written"]
    write_landmark_report(summary_for_report, rep_dir)

    logger.info(
        "Landmark extraction complete: %d detected, %d no-hand, %d errors (of %d frames)",
        detected,
        no_hand,
        errors,
        len(frame_files),
    )
    return manifest
