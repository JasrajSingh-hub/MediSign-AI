"""Filesystem I/O helpers for the Emergency Gesture Recognition module.

Kept dependency-free (standard library only) so it is importable in minimal
environments. Video decoding and image processing live in dedicated utility
modules that import OpenCV lazily.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence


def ensure_dir(path) -> Path:
    """Create ``path`` (and parents) if missing and return it as a Path.

    Parameters
    ----------
    path: str | Path
        Directory to create.

    Returns
    -------
    Path
        The resolved directory path.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_video_paths(directory: str | Path, extensions: Sequence[str] | None = None) -> List[Path]:
    """Recursively list video files under ``directory``.

    Extension matching is case-insensitive (``.avi`` matches ``.AVI``), which is
    required because the raw SOS dataset mixes ``.avi`` and ``.AVI``.

    Parameters
    ----------
    directory:
        Root directory to scan.
    extensions:
        Allowed lowercase extensions (without dots), e.g. ``["avi"]``. When
        ``None``, the extensions from the configuration are used.

    Returns
    -------
    list[Path]
        Sorted list of matching video file paths.
    """
    root = Path(directory)
    if extensions is None:
        from config import settings as _settings
        extensions = _settings.get_settings()["dataset"]["video_extensions"]
    wanted = {ext.lower().lstrip(".") for ext in extensions}
    found: List[Path] = []
    if not root.exists():
        return found
    for item in root.rglob("*"):
        if item.is_file() and item.suffix.lower().lstrip(".") in wanted:
            found.append(item)
    return sorted(found)


def read_class_directories(root: str | Path, classes: Iterable[str]) -> dict[str, List[Path]]:
    """Map each class label to the video paths found under ``root/<class>/``.

    Parameters
    ----------
    root:
        Dataset root containing one subdirectory per class.
    classes:
        Iterable of class labels to look for.

    Returns
    -------
    dict[str, list[Path]]
        Class label -> list of video paths (empty list when a class folder is
        absent or contains no videos).
    """
    root_path = Path(root)
    result: dict[str, List[Path]] = {}
    for label in classes:
        class_dir = root_path / label
        result[label] = read_video_paths(class_dir) if class_dir.is_dir() else []
    return result


def safe_filename(path: str | Path, max_length: int = 200) -> str:
    """Return a filesystem-safe stem derived from ``path``.

    Replaces characters that are invalid on common operating systems and trims
    the result to ``max_length`` characters.
    """
    stem = Path(path).stem
    unsafe = '\\/:*?"<>|'
    cleaned = "".join("_" if ch in unsafe else ch for ch in stem)
    return cleaned[:max_length] or "file"
