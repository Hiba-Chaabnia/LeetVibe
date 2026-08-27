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
import uuid
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
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

# ── Local retry queue for failed saves (offline, expired token, etc.) ─────────
# save_messages() has no other durability: a failed write previously just lost
# that turn silently. Failed attempts are cached here and retried by
# flush_pending_saves() (called at app startup) instead.
_PENDING_PATH = Path.home() / ".leetvibe" / "pending_sync.json"
_PENDING_MAX_AGE = 30 * 24 * 60 * 60  # seconds — stop retrying after this long


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

def upsert_session(
    problem_slug: str, difficulty: str, mode: str, workflow_version: str | None
) -> tuple[str | None, bool]:
    """Get or create the chat_sessions document for the current user + problem + mode.

    Returns (doc_id, stale). doc_id is None if the user is not logged in.
    stale is True when a prior session exists but was saved under a different
    workflow_version — its saved messages no longer match the current prompt
    contract, so the caller should reset_session(manual=False) before resuming
    from them. The doc is stamped with the current workflow_version either
    way, so a stale session reads as fresh again once the caller has reset it.

    workflow_version is None for modes whose saved history is never resumed
    (e.g. interview) — compatibility doesn't apply, so the field is left
    unset and stale is always False.
    """
    headers, user_id = _get_context()
    if headers is None:
        return None, False

    doc_id = f"{user_id}__{problem_slug}__{mode}"
    try:
        existing = _get_doc("chat_sessions", doc_id, headers)
        stale = (
            workflow_version is not None
            and existing is not None
            and existing.get("workflow_version") != workflow_version
        )
        data: dict[str, Any] = {
            "user_id": user_id,
            "problem_slug": problem_slug,
            "difficulty": difficulty,
            "mode": mode,
            "updated_at": _now(),
        }
        if workflow_version is not None:
            data["workflow_version"] = workflow_version
        if existing is None:
            data["reset_count"] = 0
        _set_doc("chat_sessions", doc_id, data, headers, merge=bool(existing))
        return doc_id, stale
    except Exception:
        return None, False


# ── Local retry queue ──────────────────────────────────────────────────────────

def _load_pending() -> dict[str, dict]:
    try:
        return json.loads(_PENDING_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_pending(pending: dict[str, dict]) -> None:
    try:
        _PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
        _PENDING_PATH.write_text(json.dumps(pending, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _queue_pending_save(session_id: str, messages: list[dict]) -> None:
    """Cache a failed save locally so flush_pending_saves() can retry it later.

    messages is always the full current conversation (never a delta), so a
    newer queued attempt for the same session simply overwrites the old one
    — there's nothing to merge.
    """
    pending = _load_pending()
    pending[session_id] = {"messages": messages, "queued_at": _now()}
    _save_pending(pending)


def _clear_pending_save(session_id: str) -> None:
    pending = _load_pending()
    if session_id in pending:
        del pending[session_id]
        _save_pending(pending)


# ── Messages ──────────────────────────────────────────────────────────────────

def _diff_existing(existing: list[dict], non_system: list[dict]) -> str:
    """Classify *existing* (already sorted by seq) against the in-memory
    *non_system* messages about to be saved:

    "remote_ahead" — Firestore already holds more messages than we're
        holding. Can happen if a locally-queued retry (flush_pending_saves,
        run at startup) races a live session that reopens the same
        problem+mode and saves fresher data first. Never overwrite something
        more complete than what we have — just leave it alone.
    "append"       — existing is exactly messages[:len(existing)] — safe to
        write just the new tail.
    "rebuild"      — anything else (corrupted seq range, content mismatch)
        — safest to delete everything and reinsert fresh.
    """
    n = len(existing)
    if n > len(non_system):
        return "remote_ahead"
    if [r.get("seq") for r in existing] != list(range(n)):
        return "rebuild"
    if all(
        existing[i].get("role") == non_system[i].get("role", "")
        and (existing[i].get("content") or "") == (non_system[i].get("content") or "")
        for i in range(n)
    ):
        return "append"
    return "rebuild"


def save_messages(session_id: str, messages: list[dict]) -> bool:
    """Persist new messages for a session, appending instead of replacing.

    The in-memory conversation only ever grows by appending — once a session
    is loaded, nothing rewrites an earlier message's content in place — so
    this writes only the messages Firestore doesn't already have, rather
    than the previous delete-everything-then-reinsert-everything approach,
    whose cost grew with the *whole* session's length on every single
    follow-up turn instead of with the size of one turn.

    Falls back to a full rewrite (delete + reinsert all) if the already-saved
    rows don't form a clean, contiguous, content-matching prefix of
    *messages* — e.g. if the append-only assumption above is ever broken by
    future code — so a bug there degrades to the old (correct, just slower)
    behaviour instead of silently diverging from what's in Firestore.
    If Firestore already holds *more* messages than we're about to save
    (e.g. a startup retry of a stale queued save racing a live session that
    already saved fresher data for the same session_id), this is a no-op
    instead — never overwrite something more complete than what we have.

    Every call still touches the session doc's updated_at, even when there
    are no new messages to write, so "last synced" stays accurate.
    System-prompt messages are skipped — they are always rebuilt locally.

    On failure (offline, expired token, Firestore error) *messages* is cached
    locally instead of being lost — see flush_pending_saves(). On success,
    any earlier queued attempt for this session is cleared.
    Returns True on success, False on any error or if not logged in.
    """
    ok = _try_save_messages(session_id, messages)
    if ok:
        _clear_pending_save(session_id)
    else:
        _queue_pending_save(session_id, messages)
    return ok


def _try_save_messages(session_id: str, messages: list[dict]) -> bool:
    """The actual Firestore write attempt — see save_messages() for the
    retry-queue wrapper around this."""
    headers, _ = _get_context()
    if headers is None:
        return False

    try:
        existing = _query("chat_messages", [{"field": "session_id", "value": session_id}], headers)
        existing.sort(key=lambda r: r.get("seq", -1))
        non_system = [m for m in messages if m.get("role", "") != "system"]

        diff = _diff_existing(existing, non_system)
        if diff == "remote_ahead":
            return True
        if diff == "append":
            writes: list[dict] = []
            seq = len(existing)
        else:  # "rebuild"
            writes = [{"delete": row["_name"]} for row in existing]
            seq = 0

        for msg in non_system[seq:]:
            row: dict[str, Any] = {
                "session_id": session_id,
                "seq": seq,
                "role": msg.get("role", ""),
                "content": msg.get("content") or "",
            }
            if msg.get("tool_calls"):
                row["tool_calls"] = msg["tool_calls"]
            if msg.get("tool_call_id"):
                row["tool_call_id"] = msg["tool_call_id"]
            if msg.get("name"):
                row["tool_name"] = msg["name"]

            doc_name = (
                f"projects/{FIREBASE_PROJECT_ID}/databases/(default)"
                f"/documents/chat_messages/{uuid.uuid4().hex}"
            )
            writes.append({"update": {"name": doc_name, "fields": _to_fs(row)["fields"]}})
            seq += 1

        session_doc = (
            f"projects/{FIREBASE_PROJECT_ID}/databases/(default)"
            f"/documents/chat_sessions/{session_id}"
        )
        writes.append({
            "update": {
                "name": session_doc,
                "fields": _to_fs({"updated_at": _now()})["fields"],
            },
            "updateMask": {"fieldPaths": ["updated_at"]},
        })

        resp = _req("POST", f"{_FS_BASE}:commit", headers, json={"writes": writes})
        return resp.status_code == 200
    except Exception:
        return False


def flush_pending_saves() -> int:
    """Retry any save_messages() calls that failed earlier (offline, expired
    token, transient Firestore error, ...) instead of leaving that history
    permanently unsynced. Intended to run once at app startup.

    Safe to call when not logged in — each retry will just fail again (via
    the same _get_context() check every other function uses) and stay
    queued for next time. A queued save older than _PENDING_MAX_AGE is
    dropped instead of retried — its conversation has likely moved on or
    been abandoned in the UI by then.
    Returns the number of sessions successfully synced.
    """
    pending = _load_pending()
    if not pending:
        return 0

    now = datetime.datetime.now(datetime.timezone.utc)
    synced = 0
    for session_id, entry in pending.items():
        try:
            age = (now - datetime.datetime.fromisoformat(entry.get("queued_at", ""))).total_seconds()
        except Exception:
            age = 0
        if age > _PENDING_MAX_AGE:
            _clear_pending_save(session_id)
            continue
        if save_messages(session_id, entry.get("messages", [])):
            synced += 1
    return synced


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


def reset_session(problem_slug: str, mode: str, *, manual: bool = True) -> bool:
    """Delete all messages for a session and record the reset.

    manual=True is a user-initiated "Reset" action and increments
    reset_count. manual=False is an automatic wipe of history that no
    longer matches the current workflow_version and increments
    auto_reset_count instead, so a silent version-bump wipe can never be
    mistaken for a deliberate reset in stats that surface reset_count.
    The chat_sessions document is kept so metadata is preserved.
    Returns True on success.
    """
    headers, user_id = _get_context()
    if headers is None:
        return False

    try:
        doc_id = f"{user_id}__{problem_slug}__{mode}"
        # A reset must also cancel any locally-queued retry from an earlier
        # failed save for this same session — otherwise flush_pending_saves()
        # can silently resurrect the exact conversation just reset (or, via
        # the auto-wipe path, resurrect pre-upgrade history the workflow-
        # version check exists specifically to keep from being resumed).
        _clear_pending_save(doc_id)

        existing = _get_doc("chat_sessions", doc_id, headers)
        if existing is None:
            return False

        field = "reset_count" if manual else "auto_reset_count"
        new_count = (existing.get(field) or 0) + 1
        msgs = _query("chat_messages", [{"field": "session_id", "value": doc_id}], headers)
        for m in msgs:
            _delete_doc(m["_name"], headers)

        _set_doc("chat_sessions", doc_id, {field: new_count, "updated_at": _now()}, headers, merge=True)
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

def _app_version() -> str:
    try:
        return version("leetvibe")
    except PackageNotFoundError:
        return "unknown"  # running from source without install metadata


def submit_feedback(
    type: str,
    message: str,
    problem_slug: str | None = None,
    session_id: str | None = None,
    app_version: str | None = None,
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
            "app_version": app_version or _app_version(),
            "created_at": _now(),
        }, headers)
        return None if ok else "Failed to submit feedback."
    except Exception as exc:
        return str(exc)
