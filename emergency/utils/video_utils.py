"""Video decoding and frame-extraction utilities (Phase 3).

OpenCV is imported **lazily** (inside functions), so this module imports and its
pure-logic helpers are testable without OpenCV installed. The actual frame
decoding requires ``cv2``; callers should handle the resulting ``ImportError``.

Design notes
------------
* Frame sampling is driven by :func:`sample_frame_indices` (pure, testable).
* Corrupted videos are detected when the capture cannot be opened or reports
  zero frames; they are skipped and reported rather than raising.
* Extraction is idempotent: a per-video output directory that already contains
  the expected number of frames is skipped unless ``overwrite=True``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import config
from config import PATHS
from utils.io_utils import ensure_dir, read_class_directories
from utils.logger import get_logger
from utils.progress import tqdm

logger = get_logger(__name__)


def sample_frame_indices(
    total_frames: int,
    video_fps: float,
    fps_target: int = 10,
    max_frames_per_video: int = 60,
) -> List[int]:
    """Compute the 0-based frame indices to extract from a video.

    Strategy
    --------
    * If the clip already fits within ``max_frames_per_video`` it is kept in
      full — downsampling short gesture clips would discard potentially
      informative frames, so we only throttle longer videos.
    * Otherwise, when the video FPS is known and positive, sample roughly
      ``fps_target`` frames per second: ``interval = max(1, round(video_fps /
      fps_target))``.
    * When FPS is unknown, distribute up to ``max_frames_per_video`` frames
      evenly across the clip.
    * Always cap at ``max_frames_per_video``.

    Parameters
    ----------
    total_frames: Total frames reported by the container.
    video_fps: Frames-per-second of the source video (0/negative => unknown).
    fps_target: Desired sampling rate (frames per second).
    max_frames_per_video: Hard cap on extracted frames per video.

    Returns
    -------
    list[int]
        Sorted, unique 0-based frame indices (empty if ``total_frames <= 0``).
    """
    if total_frames <= 0:
        return []
    # Short clip: keep every frame rather than sampling data away.
    if total_frames <= max(1, max_frames_per_video):
        return list(range(total_frames))
    if video_fps and video_fps > 0:
        interval = max(1, round(video_fps / max(1, fps_target)))
        indices = list(range(0, total_frames, interval))
    else:
        step = max(1, total_frames // max(1, max_frames_per_video))
        indices = list(range(0, total_frames, step))
    return indices[: max(1, max_frames_per_video)]


def build_frame_path(
    out_dir: str | Path,
    label: str,
    video_stem: str,
    frame_idx: int,
    img_ext: str = "jpg",
) -> Path:
    """Return the output path for a single extracted frame."""
    ext = img_ext.lstrip(".")
    return Path(out_dir) / label / video_stem / f"frame_{frame_idx:05d}.{ext}"


def _open_capture(video_path: Path):
    """Open a video with OpenCV, raising ``ImportError`` if cv2 is missing."""
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        raise IOError(f"Cannot open video: {video_path}")
    return cap


def extract_video_frames(
    video_path: str | Path,
    out_dir: str | Path,
    *,
    label: str = "",
    fps_target: int = 10,
    max_frames_per_video: int = 60,
    img_ext: str = "jpg",
    overwrite: bool = False,
) -> Dict[str, object]:
    """Extract sampled frames from a single video to ``out_dir/<label>/<stem>/``.

    Returns a summary dict including ``corrupted`` (bool) and ``frames_written``.
    Corrupted/unopenable videos (and a missing OpenCV install) are reported, not
    raised.
    """
    video_path = Path(video_path)
    video_stem = video_path.stem
    dest_dir = Path(out_dir) / label / video_stem
    summary: Dict[str, object] = {
        "label": label,
        "video": str(video_path),
        "video_stem": video_stem,
        "corrupted": False,
        "frames_written": 0,
        "skipped_existing": False,
        "out_dir": str(dest_dir),
    }

    # OpenCV is imported lazily; a missing install is treated as a skippable
    # (corrupted) video rather than a hard failure of the whole batch.
    try:
        import cv2
    except ImportError as exc:
        summary["corrupted"] = True
        summary["error"] = f"OpenCV (cv2) not installed: {exc}"
        logger.warning("Skipping %s (OpenCV not installed)", video_path)
        return summary

    try:
        cap = _open_capture(video_path)
    except (ImportError, IOError) as exc:
        summary["corrupted"] = True
        summary["error"] = str(exc)
        logger.warning("Skipping corrupted/unopenable video %s: %s", video_path, exc)
        return summary

    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        indices = sample_frame_indices(total, fps, fps_target, max_frames_per_video)
        wanted = set(indices)

        # Idempotency: skip if the expected frames already exist.
        if not overwrite and wanted:
            existing = {
                p.stem for p in dest_dir.glob(f"*.{img_ext.lstrip('.')}") if p.is_file()
            }
            if len(existing) >= len(wanted):
                summary["skipped_existing"] = True
                summary["frames_written"] = len(existing)
                logger.info("Already extracted %s (%d frames); skipping", video_stem, len(existing))
                return summary

        ensure_dir(dest_dir)
        written = 0
        current = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if current in wanted:
                out_path = build_frame_path(out_dir, label, video_stem, current, img_ext)
                if not cv2.imwrite(str(out_path), frame):
                    logger.warning("imwrite failed for %s", out_path)
                else:
                    written += 1
            current += 1
            if current > max(wanted):
                break
        summary["frames_written"] = written
        logger.info("Extracted %d frames from %s", written, video_stem)
        return summary
    finally:
        cap.release()


def extract_dataset_frames(
    root: Optional[str | Path] = None,
    out_dir: Optional[str | Path] = None,
    *,
    classes: Optional[List[str]] = None,
    extensions: Optional[List[str]] = None,
    fps_target: Optional[int] = None,
    max_frames_per_video: Optional[int] = None,
    img_ext: str = "jpg",
    overwrite: bool = False,
    progress: bool = True,
) -> Dict[str, object]:
    """Extract frames from every video in the dataset.

    Writes a ``manifest.json`` into ``out_dir`` capturing per-video results so
    downstream phases (landmark extraction) know exactly which frames exist.

    Returns an aggregate summary dict.
    """
    cfg = config.CONFIG
    root_path = Path(root) if root else PATHS["sos_dataset"]
    out_path = Path(out_dir) if out_dir else PATHS["frames_dir"]
    classes = classes or list(cfg["dataset"]["classes"])
    extensions = extensions or list(cfg["dataset"]["video_extensions"])
    fe = cfg["frame_extraction"]
    fps_target = fps_target if fps_target is not None else int(fe["fps_target"])
    max_frames = max_frames_per_video if max_frames_per_video is not None else int(fe["max_frames_per_video"])

    class_dirs = read_class_directories(root_path, classes)
    plan: List[Tuple[str, Path]] = []
    for label in classes:
        for vp in class_dirs[label]:
            plan.append((label, vp))

    videos_payload: List[Dict[str, object]] = []
    total_written = 0
    corrupted = 0
    skipped = 0
    iterator: Iterable[Tuple[str, Path]] = plan
    if progress:
        iterator = tqdm(plan, desc="Extracting frames", unit="video")
    for label, vp in iterator:
        res = extract_video_frames(
            vp,
            out_path,
            label=label,
            fps_target=fps_target,
            max_frames_per_video=max_frames,
            img_ext=img_ext,
            overwrite=overwrite,
        )
        videos_payload.append(res)
        total_written += int(res["frames_written"])
        if bool(res["corrupted"]):
            corrupted += 1
        if bool(res.get("skipped_existing")):
            skipped += 1

    manifest = {
        "fps_target": fps_target,
        "max_frames_per_video": max_frames,
        "img_ext": img_ext.lstrip("."),
        "dataset_root": str(root_path),
        "frames_dir": str(out_path),
        "summary": {
            "total_videos": len(plan),
            "extracted": len(plan) - corrupted,
            "corrupted": corrupted,
            "skipped_existing": skipped,
            "total_frames_written": total_written,
        },
        "videos": videos_payload,
    }
    ensure_dir(out_path)
    (out_path / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    logger.info(
        "Frame extraction complete: %d videos, %d frames written, %d corrupted, %d skipped",
        len(plan),
        total_written,
        corrupted,
        skipped,
    )
    return manifest
