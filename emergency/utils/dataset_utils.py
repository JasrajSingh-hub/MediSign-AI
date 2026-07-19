"""Dataset analysis utilities for the Emergency Gesture Recognition module.

Provides a reusable, dependency-light scanner that builds a structured report of
the raw ``SOS/`` video dataset. Video *metadata* (frame count, fps, resolution)
is extracted lazily with OpenCV when it is installed; without it the report still
contains the full structural analysis (per-class file counts, sizes, extensions)
and clearly flags that metadata was not extracted.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from config import PATHS
from utils.io_utils import ensure_dir, read_class_directories
from utils.logger import get_logger

logger = get_logger(__name__)


def _cv2_available() -> bool:
    """Return ``True`` if OpenCV can be imported in this environment."""
    try:
        import cv2  # noqa: F401
        return True
    except ImportError:
        return False


def _probe_video(video_path: Path) -> Dict[str, Any]:
    """Open ``video_path`` with OpenCV and return its metadata.

    Returns a mapping with ``corrupted`` set when the file cannot be opened or
    reports zero frames. Failures are captured rather than raised so a single bad
    file never aborts the whole scan.
    """
    import cv2

    record: Dict[str, Any] = {}
    cap = cv2.VideoCapture(str(video_path))
    try:
        if not cap.isOpened():
            record["corrupted"] = True
            record["open_error"] = "VideoCapture failed to open"
            return record
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        record.update(
            {
                "fps": round(float(fps), 3) if fps else None,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "duration_sec": round(frame_count / float(fps), 3) if fps else None,
                "corrupted": frame_count <= 0,
            }
        )
        return record
    except Exception as exc:  # pragma: no cover - defensive
        record["corrupted"] = True
        record["open_error"] = str(exc)
        return record
    finally:
        cap.release()


def scan_videos(
    root: str | Path,
    classes: Optional[List[str]] = None,
    extensions: Optional[List[str]] = None,
    probe_metadata: bool = True,
) -> Dict[str, Any]:
    """Scan the dataset and return a structured report dictionary.

    Parameters
    ----------
    root:
        Dataset root containing one subdirectory per class.
    classes:
        Class labels to scan (defaults to ``config``).
    extensions:
        Allowed video extensions (defaults to ``config``).
    probe_metadata:
        When ``True`` and OpenCV is available, enrich each video with frame/fps/
        resolution metadata and a corruption flag.

    Returns
    -------
    dict
        Report with ``summary``, ``per_class``, and ``notes`` keys.
    """
    cfg = config.CONFIG
    root_path = Path(root)
    classes = classes or list(cfg["dataset"]["classes"])
    extensions = extensions or list(cfg["dataset"]["video_extensions"])

    cv2_usable = _cv2_available() if probe_metadata else False
    notes: List[str] = []

    class_dirs = read_class_directories(root_path, classes)
    per_class: Dict[str, Any] = {}
    total_videos = 0
    total_bytes = 0
    corrupted_files: List[str] = []

    if probe_metadata and not cv2_usable:
        notes.append(
            "Video metadata (fps / frame count / resolution) was NOT extracted "
            "because OpenCV ('cv2') is not installed. Install dependencies to "
            "enable full metadata. Structural analysis is complete."
        )

    for label in classes:
        video_paths = class_dirs[label]
        videos: List[Dict[str, Any]] = []
        for p in video_paths:
            rec: Dict[str, Any] = {
                "path": str(p),
                "size_bytes": p.stat().st_size,
                "extension": p.suffix.lower(),
            }
            if cv2_usable:
                rec.update(_probe_video(p))
                if rec.get("corrupted"):
                    corrupted_files.append(str(p))
            videos.append(rec)

        ext_counts: Dict[str, int] = {}
        for rec in videos:
            ext = rec["extension"]
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

        class_size = sum(rec["size_bytes"] for rec in videos)
        per_class[label] = {
            "video_count": len(videos),
            "total_size_bytes": class_size,
            "extensions": ext_counts,
            "videos": videos,
        }
        total_videos += len(videos)
        total_bytes += class_size

    if cv2_usable:
        notes.append(f"Video metadata extracted with OpenCV; {len(corrupted_files)} corrupted file(s) detected.")

    report = {
        "module": cfg["project"]["name"],
        "dataset_root": str(root_path),
        "classes": list(classes),
        "video_extensions": list(extensions),
        "metadata_available": cv2_usable,
        "summary": {
            "total_videos": total_videos,
            "total_size_bytes": total_bytes,
            "classes_count": len(classes),
            "corrupted_count": len(corrupted_files),
            "corrupted_files": corrupted_files,
        },
        "per_class": per_class,
        "notes": notes,
    }
    return report


def _format_size(num_bytes: int) -> str:
    """Human-readable byte size (B / KB / MB / GB)."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


def render_markdown(report: Dict[str, Any]) -> str:
    """Render the report dictionary as Markdown."""
    summary = report["summary"]
    lines: List[str] = []
    lines.append("# Dataset Analysis Report — Emergency Gesture Recognition")
    lines.append("")
    lines.append(f"- **Module:** {report['module']}")
    lines.append(f"- **Dataset root:** `{report['dataset_root']}`")
    lines.append(f"- **Classes:** {', '.join(report['classes'])}")
    lines.append(f"- **Video extensions:** {', '.join(report['video_extensions'])}")
    lines.append(f"- **Metadata extracted:** {'yes' if report['metadata_available'] else 'no (OpenCV not installed)'}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total videos:** {summary['total_videos']}")
    lines.append(f"- **Total size:** {_format_size(summary['total_size_bytes'])}")
    lines.append(f"- **Classes:** {summary['classes_count']}")
    lines.append(f"- **Corrupted videos:** {summary['corrupted_count']}")
    lines.append("")
    lines.append("## Per-class breakdown")
    lines.append("")
    lines.append("| Class | Videos | Total size | Extensions | Corrupted |")
    lines.append("|-------|-------:|-----------:|------------|----------:|")
    for label in report["classes"]:
        c = report["per_class"].get(label, {})
        exts = ", ".join(f"{k}:{v}" for k, v in c.get("extensions", {}).items())
        corrupted = 0
        if report["metadata_available"]:
            corrupted = sum(1 for v in c.get("videos", []) if v.get("corrupted"))
        lines.append(
            f"| {label} | {c.get('video_count', 0)} | {_format_size(c.get('total_size_bytes', 0))} | {exts} | {corrupted} |"
        )
    lines.append("")
    if report["notes"]:
        lines.append("## Notes")
        lines.append("")
        for note in report["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines)


def write_reports(
    report: Dict[str, Any], report_dir: str | Path
) -> tuple[Path, Path]:
    """Write ``dataset_report.json`` and ``dataset_report.md``.

    Returns the (markdown_path, json_path) tuple.
    """
    out_dir = ensure_dir(report_dir)
    json_path = out_dir / "dataset_report.json"
    md_path = out_dir / "dataset_report.md"

    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    logger.info("Wrote dataset report -> %s and %s", md_path, json_path)
    return md_path, json_path


def analyze(root: Optional[str | Path] = None, report_dir: Optional[str | Path] = None) -> Dict[str, Any]:
    """Convenience entry point: scan then write reports; return the report dict."""
    dataset_root = Path(root) if root else PATHS["sos_dataset"]
    out_dir = Path(report_dir) if report_dir else PATHS["reports_dir"]
    logger.info("Analyzing dataset at %s", dataset_root)
    report = scan_videos(dataset_root)
    write_reports(report, out_dir)
    return report
