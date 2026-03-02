"""Supabase auth — sign in / sign up / session persistence.

SUPABASE_URL and SUPABASE_ANON_KEY are YOUR backend credentials, not the
user's. They are the same for every person who installs LeetVibe and are safe
to commit — the anon key is public by design and protected by Row Level Security.

How to fill them in:
    Supabase dashboard → Settings → API → Project URL + anon/public key
    Then replace the placeholder strings below and commit.
"""

from __future__ import annotations

import http.server
import json
import os
import socket
import threading
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SESSION_PATH = Path.home() / ".leetvibe" / "session.json"

# ── Credentials ───────────────────────────────────────────────────────────────
# These are baked into the published library — replace before publishing.
# Safe to commit: the anon key is intentionally public (RLS enforces access).
# During local development you can override via SUPABASE_URL / SUPABASE_ANON_KEY
# env vars in your .env file.

SUPABASE_URL: str = os.environ.get("SUPABASE_URL") or "https://rtjnkgyirapcjfuzltbl.supabase.co"
SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY") or "sb_publishable_DWjUciUOifxIQdbJ0wliuw_gHQeiK4x"


# ── Result / state types ──────────────────────────────────────────────────────

@dataclass
class AuthResult:
    ok: bool
    error: str | None = None
    user_id: str | None = None
    email: str | None = None


@dataclass
class GoogleAuthState:
    """Holds live state for an in-progress Google OAuth flow."""
    oauth_url: str                                    # open this in the browser
    port: int                                         # local callback server port
    done: threading.Event = field(default_factory=threading.Event)
    result: AuthResult | None = None
    _supabase: Any = field(default=None, repr=False)  # kept alive for code exchange


# ── Public API ────────────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> AuthResult:
    """Create a new account and sign in immediately."""
    client = _client()
    if client is None:
        return AuthResult(ok=False, error="Supabase is not configured.")
    try:
        res = client.auth.sign_up({"email": email, "password": password})
        if res.user is None:
            return AuthResult(ok=False, error="Sign up failed. Try again.")
        if res.session:
            _save_session(res)
            return AuthResult(ok=True, user_id=str(res.user.id), email=res.user.email)
        # No session yet — sign in immediately to obtain one
        return sign_in(email, password)
    except Exception as exc:
        return AuthResult(ok=False, error=_friendly(exc))


def sign_in(email: str, password: str) -> AuthResult:
    """Sign in with email and password."""
    client = _client()
    if client is None:
        return AuthResult(ok=False, error="Supabase is not configured.")
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user is None or res.session is None:
            return AuthResult(ok=False, error="Invalid credentials.")
        _save_session(res)
        return AuthResult(ok=True, user_id=str(res.user.id), email=res.user.email)
    except Exception as exc:
        return AuthResult(ok=False, error=_friendly(exc))


def load_session() -> dict | None:
    """Return the saved session dict or None if not logged in."""
    if not _SESSION_PATH.exists():
        return None
    try:
        return json.loads(_SESSION_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_logged_in() -> bool:
    """Return True if a local session file exists (fast, no network call)."""
    return bool(load_session())


def clear_session() -> None:
    """Remove the saved session (logout)."""
    try:
        _SESSION_PATH.unlink(missing_ok=True)
    except Exception:
        pass


# ── Google OAuth ──────────────────────────────────────────────────────────────
# Requirements (one-time Supabase setup):
#   Dashboard → Authentication → Providers → Google → enable
#   Paste your Google Cloud OAuth Client ID + Secret
#   Add "http://127.0.0.1" to the allowed redirect URLs  (Supabase accepts any port)

def start_google_auth() -> GoogleAuthState | AuthResult:
    """Prepare the Google OAuth flow.

    Returns a GoogleAuthState whose ``oauth_url`` should be opened in the
    browser.  Block on ``state.done`` (e.g. via asyncio.to_thread) and then
    read ``state.result``.  Returns AuthResult(ok=False) on config errors.
    """
    client = _client()
    if client is None:
        return AuthResult(ok=False, error="Supabase is not configured.")

    # Pick a free ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    state = GoogleAuthState(oauth_url="", port=port, _supabase=client)

    try:
        res = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": f"https://hiba-chaabnia.github.io/LeetVibe/?port={port}"},
        })
        state.oauth_url = res.url
    except Exception as exc:
        return AuthResult(ok=False, error=_friendly(exc))

    _start_callback_server(state)
    return state


_PAGES_URL = "https://hiba-chaabnia.github.io/LeetVibe/"


def _start_callback_server(state: GoogleAuthState) -> None:
    """Spin up a one-shot HTTP server in a daemon thread to catch the OAuth redirect."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/result"):
                params = dict(urllib.parse.parse_qsl(
                    urllib.parse.urlparse(self.path).query
                ))
                _resolve(state, params)
                # Redirect the browser back to GitHub Pages to show the result
                location = _PAGES_URL + ("?auth=done" if state.result and state.result.ok else "?auth=error")
                self.send_response(302)
                self.send_header("Location", location)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *_):
            pass  # silence access logs

    server = http.server.HTTPServer(("127.0.0.1", state.port), _Handler)

    def _serve():
        # handle_request() blocks until one request arrives; loop until done
        while not state.done.is_set():
            server.handle_request()
        server.server_close()

    threading.Thread(target=_serve, daemon=True).start()


def _resolve(state: GoogleAuthState, params: dict) -> None:
    """Called from the HTTP handler thread once the callback params arrive."""
    if "error" in params:
        state.result = AuthResult(ok=False, error=params["error"])
        state.done.set()
        return

    try:
        access_token = params.get("access_token")
        refresh_token = params.get("refresh_token", "")
        code = params.get("code")

        if access_token:
            # Implicit flow — tokens are in the URL hash
            res = state._supabase.auth.set_session(access_token, refresh_token)
        elif code:
            # PKCE flow — exchange the authorisation code
            res = state._supabase.auth.exchange_code_for_session({"auth_code": code})
        else:
            state.result = AuthResult(ok=False, error="No credentials received from Google.")
            state.done.set()
            return

        if res.user is None:
            state.result = AuthResult(ok=False, error="Google sign-in failed.")
        else:
            _save_session(res)
            state.result = AuthResult(ok=True, user_id=str(res.user.id), email=res.user.email)
    except Exception as exc:
        state.result = AuthResult(ok=False, error=_friendly(exc))
    finally:
        state.done.set()


# ── Internals ─────────────────────────────────────────────────────────────────

def _client():
    """Return a Supabase client, or None if credentials are not set."""
    if not SUPABASE_URL or "your-project" in SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def _save_session(res) -> None:
    session = res.session
    if not session:
        return
    _SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SESSION_PATH.write_text(
        json.dumps({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user_id": str(res.user.id),
            "email": res.user.email,
        }),
        encoding="utf-8",
    )


def _friendly(exc: Exception) -> str:
    """Convert a Supabase / network exception to a short user-readable string."""
    msg = str(exc)
    # gotrue returns messages like: "Invalid login credentials"
    if "Invalid login credentials" in msg:
        return "Wrong email or password."
    if "User already registered" in msg:
        return "An account with this email already exists."
    if "Password should be" in msg:
        return "Password must be at least 6 characters."
    if "Unable to validate" in msg or "network" in msg.lower():
        return "Network error. Check your connection and try again."
    if "email rate limit" in msg.lower():
        return "Too many sign-up attempts. Please wait a few minutes and try again."
    # Fall back to the raw message, capped at 80 chars
    return msg[:80]
