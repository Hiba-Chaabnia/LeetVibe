"""Update check — detects when a newer LeetVibe release is on PyPI.

Runs in a background thread at app startup; never blocks, never raises.
The PyPI response is cached in ~/.leetvibe/update_check.json for 24 hours
so we hit the network at most once a day.
"""

from __future__ import annotations

import json
import time
import urllib.request
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

_CACHE_PATH = Path.home() / ".leetvibe" / "update_check.json"
_CACHE_TTL = 24 * 60 * 60  # seconds
_PYPI_URL = "https://pypi.org/pypi/leetvibe/json"
_TIMEOUT = 5  # seconds


def _parse(v: str) -> tuple[int, ...]:
    """Best-effort version tuple: '0.1.10' → (0, 1, 10). Non-numeric parts → 0."""
    parts: list[int] = []
    for part in v.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _cached_latest() -> str | None:
    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        if time.time() - float(data["checked_at"]) < _CACHE_TTL:
            return str(data["latest"])
    except Exception:
        pass
    return None


def _fetch_latest() -> str | None:
    try:
        with urllib.request.urlopen(_PYPI_URL, timeout=_TIMEOUT) as resp:
            latest = json.load(resp)["info"]["version"]
    except Exception:
        return None
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(
            json.dumps({"checked_at": time.time(), "latest": latest}),
            encoding="utf-8",
        )
    except Exception:
        pass
    return latest


def check_for_update() -> str | None:
    """Return the newer PyPI version string if one exists, else None.

    Does network and disk I/O — call from a background thread only.
    """
    try:
        current = version("leetvibe")
    except PackageNotFoundError:
        return None  # running from source without install metadata
    latest = _cached_latest() or _fetch_latest()
    if latest and _parse(latest) > _parse(current):
        return latest
    return None
