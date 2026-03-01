"""Development session logger.

Appends one JSON-Lines entry per agent session to logs/sessions.log.
Each entry contains: timestamp, challenge info, mode, full output text,
duration, tool calls made, and any error.

Usage (called automatically from AgentSessionScreen._run_agent):
    from src.session_log import SessionLog
    log = SessionLog(challenge, mode, user_code)
    log.record_chunk(chunk)       # call for each streamed chunk
    log.finish(error=None)        # call when session ends
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

_LOG_FILE = Path(__file__).parent.parent / "logs" / "sessions.log"


def _strip_markup(text: str) -> str:
    """Remove Rich markup tags from text for clean log output."""
    return re.sub(r"\[/?[a-zA-Z#/ ][^\[\]]*\]", "", text)


class SessionLog:
    def __init__(self, challenge, mode: str, user_code: str) -> None:
        self._challenge = challenge
        self._mode = mode
        self._has_user_code = bool(user_code.strip())
        self._start = time.monotonic()
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._chunks: list[str] = []
        # Each entry: {"name": str, "ok": bool, "error": str | None}
        self._tool_calls: list[dict] = []

    def record_chunk(self, chunk: str) -> None:
        """Accumulate a streamed chunk and extract tool-call metadata."""
        self._chunks.append(chunk)

        # "⚙  Calling run_code…" → new tool call entry
        m = re.search(r"⚙\s+Calling\s+(\w+)", chunk)
        if m:
            self._tool_calls.append({"name": m.group(1), "ok": True, "error": None})
            return

        # "   → {…}" → result preview for the last tool call
        if self._tool_calls and re.search(r"→\s+\S", chunk):
            preview = _strip_markup(chunk).strip().lstrip("→").strip()
            try:
                data = json.loads(preview)
                if isinstance(data, dict) and "error" in data:
                    self._tool_calls[-1]["ok"] = False
                    self._tool_calls[-1]["error"] = data["error"]
            except Exception:
                # preview is truncated or not JSON — check for "error" keyword
                if '"error"' in preview:
                    self._tool_calls[-1]["ok"] = False
                    self._tool_calls[-1]["error"] = preview[:200]

    def finish(self, error: str | None = None) -> None:
        """Write the completed session entry to logs/sessions.log."""
        elapsed = round(time.monotonic() - self._start, 1)
        full_text = _strip_markup("".join(self._chunks))
        ch = self._challenge

        entry = {
            "ts": self._started_at,
            "challenge_id": ch.id,
            "challenge_title": ch.title,
            "difficulty": ch.difficulty,
            "mode": self._mode,
            "has_user_code": self._has_user_code,
            "duration_s": elapsed,
            "tool_calls": self._tool_calls,
            "tool_errors": [t for t in self._tool_calls if not t["ok"]],
            "output_chars": len(full_text),
            "output": full_text,
            "error": error,
        }

        try:
            _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with _LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # never crash the session because logging failed
