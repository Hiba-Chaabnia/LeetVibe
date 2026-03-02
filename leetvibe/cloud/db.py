"""Supabase database operations — chat history, progress, feedback.

All public functions are safe to call even when the user is not logged in:
they return empty/False/None rather than raising.  Network or auth errors
are swallowed silently so they never crash the TUI.
"""

from __future__ import annotations

from typing import Any


# ── Auth helper ───────────────────────────────────────────────────────────────

def _authed_client():
    """Return a Supabase client authenticated as the current user, or None."""
    from .auth import _client, load_session

    supabase = _client()
    if supabase is None:
        return None

    session = load_session()
    if not session:
        return None

    try:
        supabase.auth.set_session(
            session["access_token"],
            session["refresh_token"],
        )
        return supabase
    except Exception:
        return None


def _current_user_id(client) -> str | None:
    try:
        resp = client.auth.get_user()
        return str(resp.user.id) if resp and resp.user else None
    except Exception:
        return None


# ── Chat sessions ─────────────────────────────────────────────────────────────

def upsert_session(problem_slug: str, difficulty: str, mode: str) -> str | None:
    """Get or create the chat_sessions row for the current user + problem + mode.

    Returns the session UUID string, or None if the user is not logged in.
    """
    client = _authed_client()
    if client is None:
        return None

    user_id = _current_user_id(client)
    if user_id is None:
        return None

    try:
        res = (
            client.table("chat_sessions")
            .upsert(
                {
                    "user_id": user_id,
                    "problem_slug": problem_slug,
                    "difficulty": difficulty,
                    "mode": mode,
                },
                on_conflict="user_id,problem_slug,mode",
            )
            .execute()
        )
        return res.data[0]["id"] if res.data else None
    except Exception:
        return None


# ── Messages ──────────────────────────────────────────────────────────────────

def save_messages(session_id: str, messages: list[dict]) -> bool:
    """Persist the full message list for a session.

    Strategy: delete all existing rows then bulk-insert the current state.
    System-prompt messages are skipped — they are always rebuilt locally.
    Returns True on success, False on any error or if not logged in.
    """
    client = _authed_client()
    if client is None:
        return False

    try:
        # Wipe existing messages for this session
        client.table("chat_messages").delete().eq("session_id", session_id).execute()

        rows: list[dict[str, Any]] = []
        seq = 0
        for msg in messages:
            role = msg.get("role", "")
            if role == "system":
                continue  # always rebuilt from prompt — no need to persist

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

            rows.append(row)
            seq += 1

        if rows:
            client.table("chat_messages").insert(rows).execute()

        # Bump the session's updated_at timestamp
        (
            client.table("chat_sessions")
            .update({"updated_at": "now()"})
            .eq("id", session_id)
            .execute()
        )

        return True
    except Exception:
        return False


def load_messages(problem_slug: str, mode: str) -> list[dict]:
    """Load saved messages for the current user's session, ordered by seq.

    Returns an empty list if the user is not logged in or no prior session exists.
    The returned dicts match the format VibeAgent uses for self._messages
    (role, content, tool_calls, tool_call_id, name).
    """
    client = _authed_client()
    if client is None:
        return []

    try:
        session_res = (
            client.table("chat_sessions")
            .select("id")
            .eq("problem_slug", problem_slug)
            .eq("mode", mode)
            .maybe_single()
            .execute()
        )
        if not session_res.data:
            return []

        session_id = session_res.data["id"]

        msg_res = (
            client.table("chat_messages")
            .select("role,content,tool_calls,tool_call_id,tool_name")
            .eq("session_id", session_id)
            .order("seq")
            .execute()
        )

        messages: list[dict] = []
        for row in msg_res.data or []:
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

    The chat_sessions row itself is kept so metadata (created_at, reset_count)
    is preserved.  Returns True on success.
    """
    client = _authed_client()
    if client is None:
        return False

    try:
        session_res = (
            client.table("chat_sessions")
            .select("id,reset_count")
            .eq("problem_slug", problem_slug)
            .eq("mode", mode)
            .maybe_single()
            .execute()
        )
        if not session_res.data:
            return False

        session_id = session_res.data["id"]
        new_count = (session_res.data.get("reset_count") or 0) + 1

        client.table("chat_messages").delete().eq("session_id", session_id).execute()
        (
            client.table("chat_sessions")
            .update({"reset_count": new_count, "updated_at": "now()"})
            .eq("id", session_id)
            .execute()
        )
        return True
    except Exception:
        return False


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_session_stats() -> dict:
    """Return aggregate stats for the current user's cloud sessions.

    Returns a dict with ``session_count`` and ``last_updated`` (ISO string or None).
    Safe to call when not logged in — returns zero values.
    """
    client = _authed_client()
    if client is None:
        return {"session_count": 0, "last_updated": None}
    try:
        res = (
            client.table("chat_sessions")
            .select("id, updated_at")
            .order("updated_at", desc=True)
            .execute()
        )
        data = res.data or []
        return {
            "session_count": len(data),
            "last_updated": data[0]["updated_at"] if data else None,
        }
    except Exception:
        return {"session_count": 0, "last_updated": None}


# ── Solved problems ───────────────────────────────────────────────────────────

def mark_solved(problem_slug: str, difficulty: str, code: str) -> bool:
    """Record that the current user solved a problem and save their code.

    Uses upsert so re-submitting an already-solved problem just updates the
    stored code rather than inserting a duplicate row.
    Returns True on success, False when not logged in or on error.
    """
    client = _authed_client()
    if client is None:
        return False
    user_id = _current_user_id(client)
    if user_id is None:
        return False
    try:
        client.table("user_solutions").upsert(
            {
                "user_id": user_id,
                "problem_slug": problem_slug,
                "difficulty": difficulty,
                "code": code,
            },
            on_conflict="user_id,problem_slug",
        ).execute()
        return True
    except Exception:
        return False


def get_solved_slugs() -> set[str]:
    """Return the set of problem slugs the current user has solved.

    Returns an empty set when not logged in or on error — callers can treat
    an empty set the same as "no solved problems yet".
    """
    client = _authed_client()
    if client is None:
        return set()
    try:
        res = client.table("user_solutions").select("problem_slug").execute()
        return {row["problem_slug"] for row in res.data or []}
    except Exception:
        return set()


# ── Feedback ──────────────────────────────────────────────────────────────────

def submit_feedback(
    type: str,
    message: str,
    problem_slug: str | None = None,
    session_id: str | None = None,
    app_version: str = "0.1.0",
) -> str | None:
    """Submit user feedback.

    Returns None on success, or an error string describing the failure.
    Works for both logged-in and anonymous users — anonymous inserts require
    a permissive RLS insert policy on the feedback table in Supabase.
    """
    client = _authed_client()
    if client is None:
        from .auth import _client as base_client
        client = base_client()
    if client is None:
        return "Supabase client not configured."

    try:
        user_id: str | None = _current_user_id(client)
        client.table("feedback").insert({
            "user_id": user_id,
            "type": type,
            "message": message,
            "problem_slug": problem_slug,
            "session_id": session_id,
            "app_version": app_version,
        }).execute()
        return None  # success
    except Exception as exc:
        return str(exc)
