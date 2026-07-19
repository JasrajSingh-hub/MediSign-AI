"""Optional progress-bar helper.

Wraps `tqdm` when it is installed; otherwise falls back to a plain iterator so
the rest of the code can use `tqdm(...)` unconditionally without taking a hard
dependency on tqdm.
"""
from __future__ import annotations

from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")

try:  # pragma: no cover - depends on environment
    from tqdm import tqdm as _tqdm

    _HAS_TQDM = True
except ImportError:  # pragma: no cover
    _HAS_TQDM = False

    def _tqdm(iterable, **_kwargs):  # type: ignore
        return iterable


def tqdm(iterable: Iterable[T], **kwargs) -> Iterator[T]:
    """Yield items from ``iterable``, showing a progress bar if tqdm is available."""
    return _tqdm(iterable, **kwargs)
