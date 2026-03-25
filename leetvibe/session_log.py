"""SessionLog — lightweight local session recorder."""

from __future__ import annotations

import json
import time
from pathlib import Path

from .problem_loader import Problem

_LOG_DIR = Path.home() / ".leetvibe" / "logs"


class SessionLog:
    """Records streaming chunks and session metadata to a local JSONL log."""

    def __init__(self, problem: Problem, mode: str, user_code: str = "") -> None:
        self._problem_id = getattr(problem, "id", None) or problem.title
        self._mode = mode
        self._user_code = user_code
        self._chunks: list[str] = []
        self._start_ts = time.time()

    def record_chunk(self, chunk: str) -> None:
        self._chunks.append(chunk)

    def finish(self, error: str | None = None) -> None:
        try:
            _LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_path = _LOG_DIR / "sessions.jsonl"
            entry = {
                "problem_id": self._problem_id,
                "mode": self._mode,
                "duration_s": round(time.time() - self._start_ts, 1),
                "chunks": len(self._chunks),
                "error": error,
                "ts": int(self._start_ts),
            }
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
