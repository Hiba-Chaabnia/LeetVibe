"""Firestore database operations via REST API — chat history, progress, feedback.

Uses the Firebase ID token from the local session to authenticate all requests.
No service account or private key is required — end users authenticate with
their own credentials and Firestore Security Rules enforce data isolation.

All public functions are safe to call when not logged in: they return
empty / False / None rather than raising. Network errors are swallowed
silently so they never crash the TUI.

Document ID conventions (deterministic, avoids extra indexes):
    chat_sessions  → "{user_id}__{problem_slug}__{mode}"
    user_solutions → "{user_id}__{problem_slug}"
"""

from __future__ import annotations

import datetime
import json
import os
from typing import Any

import requests as _requests

FIREBASE_PROJECT_ID: str = (
    os.environ.get("FIREBASE_PROJECT_ID") or "leetvibe-e6a16"
)
_FS_BASE = (
    f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}"
    "/databases/(default)/documents"
)

# Fields stored as JSON strings (complex nested structures)
_JSON_FIELDS = {"tool_calls"}


# ── Firestore value encoding / decoding ───────────────────────────────────────

def _encode(value: Any) -> dict:
    if value is None:
        return {"nullValue": None}
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    # Lists and dicts fall back to JSON string
    return {"stringValue": json.dumps(value)}


def _decode(typed: dict) -> Any:
    if "nullValue" in typed:
        return None
    if "booleanValue" in typed:
        return typed["booleanValue"]
    if "integerValue" in typed:
        return int(typed["integerValue"])
    if "doubleValue" in typed:
        return typed["doubleValue"]
    if "stringValue" in typed:
        return typed["stringValue"]
    if "arrayValue" in typed:
        return [_decode(v) for v in typed.get("arrayValue", {}).get("values", [])]
    if "mapValue" in typed:
        return {k: _decode(v) for k, v in typed.get("mapValue", {}).get("fields", {}).items()}
    return None


def _to_fs(data: dict) -> dict:
    fields = {}
    for k, v in data.items():
        if v is None:
            continue
        if k in _JSON_FIELDS and isinstance(v, (list, dict)):
            fields[k] = {"stringValue": json.dumps(v)}
        else:
            fields[k] = _encode(v)
    return {"fields": fields}


def _from_fs(doc: dict) -> dict:
    result = {}
    for k, v in doc.get("fields", {}).items():
        val = _decode(v)
        if k in _JSON_FIELDS and isinstance(val, str):
            try:
                val = json.loads(val)
            except Exception:
                pass
        result[k] = val
    return result


# ── Auth context ──────────────────────────────────────────────────────────────

def _get_context() -> tuple[dict, str] | tuple[None, None]:
    """Return (auth_headers, user_id) or (None, None)."""
    from .auth import load_session

    session = load_session()
    if not session:
        return None, None
    user_id = session.get("user_id", "")
    id_token = session.get("id_token", "")
    if not user_id or not id_token:
        return None, None
    return {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}, user_id


def _req(method: str, url: str, headers: dict, **kwargs) -> _requests.Response:
    """Make a Firestore REST request, auto-refreshing the ID token on 401."""
    resp = _requests.request(method, url, headers=headers, timeout=10, **kwargs)
    if resp.status_code == 401:
        from .auth import _refresh_id_token
        new_token = _refresh_id_token()
        if new_token:
            headers = {**headers, "Authorization": f"Bearer {new_token}"}
            resp = _requests.request(method, url, headers=headers, timeout=10, **kwargs)
    return resp


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ── Low-level Firestore helpers ───────────────────────────────────────────────

def _get_doc(collection: str, doc_id: str, headers: dict) -> dict | None:
    resp = _req("GET", f"{_FS_BASE}/{collection}/{doc_id}", headers)
    if resp.status_code == 200:
        return _from_fs(resp.json())
    return None


def _set_doc(collection: str, doc_id: str, data: dict, headers: dict, merge: bool = False) -> bool:
    body = _to_fs(data)
    if merge:
        mask = "&".join(f"updateMask.fieldPaths={k}" for k in data if data[k] is not None)
        url = f"{_FS_BASE}/{collection}/{doc_id}?{mask}"
    else:
        url = f"{_FS_BASE}/{collection}/{doc_id}"
    resp = _req("PATCH", url, headers, json=body)
    return resp.status_code in (200, 201)


def _add_doc(collection: str, data: dict, headers: dict) -> bool:
    resp = _req("POST", f"{_FS_BASE}/{collection}", headers, json=_to_fs(data))
    return resp.status_code in (200, 201)


def _delete_doc(resource_name: str, headers: dict) -> None:
    """Delete by full Firestore resource name (from query results)."""
    url = f"https://firestore.googleapis.com/v1/{resource_name}"
    _req("DELETE", url, headers)


def _query(collection: str, filters: list[dict], headers: dict) -> list[dict]:
    """Run a structured equality query.

    filters: [{"field": "field_name", "value": value}, ...]
    Returns list of dicts with an extra ``_name`` key for deletion.
    """
    if len(filters) == 1:
        where: dict = {
            "fieldFilter": {
                "field": {"fieldPath": filters[0]["field"]},
                "op": "EQUAL",
                "value": _encode(filters[0]["value"]),
            }
        }
    else:
        where = {
            "compositeFilter": {
                "op": "AND",
                "filters": [
                    {"fieldFilter": {
                        "field": {"fieldPath": f["field"]},
                        "op": "EQUAL",
                        "value": _encode(f["value"]),
                    }}
                    for f in filters
                ],
            }
        }

    body = {"structuredQuery": {"from": [{"collectionId": collection}], "where": where}}
    resp = _req("POST", f"{_FS_BASE}:runQuery", headers, json=body)
    if resp.status_code != 200:
        return []

    results = []
    for item in resp.json():
        doc = item.get("document")
        if doc and "fields" in doc:
            row = _from_fs(doc)
            row["_name"] = doc["name"]
            results.append(row)
    return results


# ── Chat sessions ─────────────────────────────────────────────────────────────

def upsert_session(problem_slug: str, difficulty: str, mode: str) -> str | None:
    """Get or create the chat_sessions document for the current user + problem + mode.

    Returns the document ID string, or None if the user is not logged in.
    """
    headers, user_id = _get_context()
    if headers is None:
        return None

    doc_id = f"{user_id}__{problem_slug}__{mode}"
    try:
        existing = _get_doc("chat_sessions", doc_id, headers)
        data: dict[str, Any] = {
            "user_id": user_id,
            "problem_slug": problem_slug,
            "difficulty": difficulty,
            "mode": mode,
            "updated_at": _now(),
        }
        if existing is None:
            data["reset_count"] = 0
        _set_doc("chat_sessions", doc_id, data, headers, merge=bool(existing))
        return doc_id
    except Exception:
        return None


# ── Messages ──────────────────────────────────────────────────────────────────

def save_messages(session_id: str, messages: list[dict]) -> bool:
    """Persist the full message list for a session.

    Strategy: delete all existing rows then bulk-insert the current state.
    System-prompt messages are skipped — they are always rebuilt locally.
    Returns True on success, False on any error or if not logged in.
    """
    headers, _ = _get_context()
    if headers is None:
        return False

    try:
        existing = _query("chat_messages", [{"field": "session_id", "value": session_id}], headers)
        for row in existing:
            _delete_doc(row["_name"], headers)

        seq = 0
        for msg in messages:
            role = msg.get("role", "")
            if role == "system":
                continue

            row: dict[str, Any] = {
                "session_id": session_id,
                "seq": seq,
                "role": role,
                "content": msg.get("content") or "",
            }
            if msg.get("tool_calls"):
                row["tool_calls"] = msg["tool_calls"]
            if msg.get("tool_call_id"):
                row["tool_call_id"] = msg["tool_call_id"]
            if msg.get("name"):
                row["tool_name"] = msg["name"]

            _add_doc("chat_messages", row, headers)
            seq += 1

        _set_doc("chat_sessions", session_id, {"updated_at": _now()}, headers, merge=True)
        return True
    except Exception:
        return False


def load_messages(problem_slug: str, mode: str) -> list[dict]:
    """Load saved messages for the current user's session, ordered by seq.

    Returns an empty list if the user is not logged in or no prior session exists.
    The returned dicts match the format VibeAgent uses for self._messages.
    """
    headers, user_id = _get_context()
    if headers is None:
        return []

    try:
        doc_id = f"{user_id}__{problem_slug}__{mode}"
        if _get_doc("chat_sessions", doc_id, headers) is None:
            return []

        rows = _query("chat_messages", [{"field": "session_id", "value": doc_id}], headers)
        rows.sort(key=lambda r: r.get("seq", 0))

        messages: list[dict] = []
        for row in rows:
            msg: dict[str, Any] = {
                "role": row["role"],
                "content": row.get("content") or "",
            }
            if row.get("tool_calls"):
                msg["tool_calls"] = row["tool_calls"]
            if row.get("tool_call_id"):
                msg["tool_call_id"] = row["tool_call_id"]
            if row.get("tool_name"):
                msg["name"] = row["tool_name"]
            messages.append(msg)

        return messages
    except Exception:
        return []


def reset_session(problem_slug: str, mode: str) -> bool:
    """Delete all messages for a session and increment reset_count.

    The chat_sessions document is kept so metadata is preserved.
    Returns True on success.
    """
    headers, user_id = _get_context()
    if headers is None:
        return False

    try:
        doc_id = f"{user_id}__{problem_slug}__{mode}"
        existing = _get_doc("chat_sessions", doc_id, headers)
        if existing is None:
            return False

        new_count = (existing.get("reset_count") or 0) + 1
        msgs = _query("chat_messages", [{"field": "session_id", "value": doc_id}], headers)
        for m in msgs:
            _delete_doc(m["_name"], headers)

        _set_doc("chat_sessions", doc_id, {"reset_count": new_count, "updated_at": _now()}, headers, merge=True)
        return True
    except Exception:
        return False


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_session_stats() -> dict:
    """Return aggregate stats for the current user's cloud sessions.

    Returns a dict with ``session_count`` and ``last_updated`` (ISO string or None).
    Safe to call when not logged in — returns zero values.
    """
    headers, user_id = _get_context()
    if headers is None:
        return {"session_count": 0, "last_updated": None}

    try:
        docs = _query("chat_sessions", [{"field": "user_id", "value": user_id}], headers)
        docs.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
        return {
            "session_count": len(docs),
            "last_updated": docs[0]["updated_at"] if docs else None,
        }
    except Exception:
        return {"session_count": 0, "last_updated": None}


# ── Solved problems ───────────────────────────────────────────────────────────

def mark_solved(problem_slug: str, difficulty: str, code: str) -> bool:
    """Record that the current user solved a problem and save their code.

    Uses set (full overwrite) so re-submitting just updates the stored code.
    Returns True on success, False when not logged in or on error.
    """
    headers, user_id = _get_context()
    if headers is None:
        return False

    try:
        doc_id = f"{user_id}__{problem_slug}"
        _set_doc("user_solutions", doc_id, {
            "user_id": user_id,
            "problem_slug": problem_slug,
            "difficulty": difficulty,
            "code": code,
            "updated_at": _now(),
        }, headers)
        return True
    except Exception:
        return False


def get_solved_slugs() -> set[str]:
    """Return the set of problem slugs the current user has solved.

    Returns an empty set when not logged in or on error.
    """
    headers, user_id = _get_context()
    if headers is None:
        return set()

    try:
        docs = _query("user_solutions", [{"field": "user_id", "value": user_id}], headers)
        return {d["problem_slug"] for d in docs}
    except Exception:
        return set()


# ── Streak ────────────────────────────────────────────────────────────────────

def get_streak_stats() -> dict:
    """Return solve-streak stats computed from user_solutions timestamps.

    Returns a dict with:
      - ``current_streak``: consecutive days ending today (or yesterday if today
        has no solve yet — the day isn't over).
      - ``longest_streak``: longest ever consecutive-day run.
      - ``last_solve_date``: YYYY-MM-DD string of the most recent solve, or None.

    Safe to call when not logged in — returns zero values.
    """
    headers, user_id = _get_context()
    if headers is None:
        return {"current_streak": 0, "longest_streak": 0, "last_solve_date": None}

    try:
        docs = _query("user_solutions", [{"field": "user_id", "value": user_id}], headers)
        if not docs:
            return {"current_streak": 0, "longest_streak": 0, "last_solve_date": None}

        # Collect unique UTC solve dates (YYYY-MM-DD)
        date_strs: set[str] = set()
        for doc in docs:
            updated = doc.get("updated_at", "")
            if updated:
                date_strs.add(updated[:10])

        if not date_strs:
            return {"current_streak": 0, "longest_streak": 0, "last_solve_date": None}

        last_solve_date = max(date_strs)

        today = datetime.datetime.now(datetime.timezone.utc).date()
        yesterday = today - datetime.timedelta(days=1)

        # Current streak: count backward from today (or yesterday if today is
        # unsolved — the day is still in progress so the streak isn't broken yet).
        if today.isoformat() in date_strs:
            start = today
        elif yesterday.isoformat() in date_strs:
            start = yesterday
        else:
            start = None

        current_streak = 0
        if start is not None:
            check = start
            while check.isoformat() in date_strs:
                current_streak += 1
                check -= datetime.timedelta(days=1)

        # Longest streak: walk sorted dates and find the longest consecutive run.
        sorted_dates = sorted(datetime.date.fromisoformat(d) for d in date_strs)
        longest_streak = 1
        run = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                run += 1
            else:
                run = 1
            if run > longest_streak:
                longest_streak = run

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_solve_date": last_solve_date,
        }
    except Exception:
        return {"current_streak": 0, "longest_streak": 0, "last_solve_date": None}


# ── Feedback ──────────────────────────────────────────────────────────────────

def submit_feedback(
    type: str,
    message: str,
    problem_slug: str | None = None,
    session_id: str | None = None,
    app_version: str = "0.2.0",
) -> str | None:
    """Submit user feedback. Returns None on success, error string on failure."""
    headers, user_id = _get_context()
    if headers is None:
        return "Not logged in."

    try:
        ok = _add_doc("feedback", {
            "user_id": user_id,
            "type": type,
            "message": message,
            "problem_slug": problem_slug,
            "session_id": session_id,
            "app_version": app_version,
            "created_at": _now(),
        }, headers)
        return None if ok else "Failed to submit feedback."
    except Exception as exc:
        return str(exc)
