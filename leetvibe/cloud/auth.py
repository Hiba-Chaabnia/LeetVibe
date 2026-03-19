"""Firebase Auth — sign in / sign up / session persistence.

Uses the Firebase Auth REST API so no service account is required.
Public credentials are baked in for published package use — they are safe
to expose (the Web API Key is protected by Firebase Security Rules and Auth
settings; the Desktop OAuth client secret is non-sensitive per Google policy).

Developers can override any value via environment variables in .env.
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

import requests

_SESSION_PATH = Path.home() / ".leetvibe" / "session.json"

# ── Baked-in public credentials ───────────────────────────────────────────────
# Safe to commit — Web API Key is public by design; Desktop OAuth client
# secret is non-sensitive (Google explicitly allows embedding it in CLI apps).

FIREBASE_WEB_API_KEY: str = (
    os.environ.get("FIREBASE_WEB_API_KEY")
    or "AIzaSyBgwPA3Vn61219NabeFbawtvxRNh5ijgME"
)
GOOGLE_CLIENT_ID: str = (
    os.environ.get("GOOGLE_CLIENT_ID")
    or "437323442448-2ufbu5rcfteh21thbf3qgprj8a99c7dp.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET: str = (
    os.environ.get("GOOGLE_CLIENT_SECRET")
    or "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"
)

_AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"
_TOKEN_BASE = "https://securetoken.googleapis.com/v1/token"

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
    oauth_url: str                                  # open this in the browser
    port: int                                       # local callback server port
    done: threading.Event = field(default_factory=threading.Event)
    result: AuthResult | None = None


# ── Public API ────────────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> AuthResult:
    """Create a new account and sign in immediately."""
    try:
        resp = requests.post(
            f"{_AUTH_BASE}:signUp",
            params={"key": FIREBASE_WEB_API_KEY},
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10,
        )
        data = resp.json()
        if "error" in data:
            return AuthResult(ok=False, error=_friendly(data["error"]))
        if not data.get("localId") or not data.get("email"):
            return AuthResult(ok=False, error="Unexpected response from auth server.")
        _save_session(data)
        return AuthResult(ok=True, user_id=data["localId"], email=data["email"])
    except Exception as exc:
        return AuthResult(ok=False, error=str(exc)[:80])


def sign_in(email: str, password: str) -> AuthResult:
    """Sign in with email and password."""
    try:
        resp = requests.post(
            f"{_AUTH_BASE}:signInWithPassword",
            params={"key": FIREBASE_WEB_API_KEY},
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10,
        )
        data = resp.json()
        if "error" in data:
            return AuthResult(ok=False, error=_friendly(data["error"]))
        if not data.get("localId") or not data.get("email"):
            return AuthResult(ok=False, error="Unexpected response from auth server.")
        _save_session(data)
        return AuthResult(ok=True, user_id=data["localId"], email=data["email"])
    except Exception as exc:
        return AuthResult(ok=False, error=str(exc)[:80])


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


def _refresh_id_token() -> str | None:
    """Refresh the Firebase ID token using the saved refresh token.

    Updates the session file and returns the new ID token, or None on failure.
    Called automatically by db.py when a 401 is received.
    """
    session = load_session()
    if not session:
        return None
    refresh_token = session.get("refresh_token", "")
    if not refresh_token:
        return None
    try:
        resp = requests.post(
            _TOKEN_BASE,
            params={"key": FIREBASE_WEB_API_KEY},
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=10,
        )
        data = resp.json()
        if "error" in data:
            return None
        new_id_token = data.get("id_token", "")
        session["id_token"] = new_id_token
        session["refresh_token"] = data.get("refresh_token", refresh_token)
        _SESSION_PATH.write_text(json.dumps(session), encoding="utf-8")
        return new_id_token
    except Exception:
        return None


# ── Google OAuth ──────────────────────────────────────────────────────────────

def start_google_auth() -> GoogleAuthState | AuthResult:
    """Prepare the Google OAuth flow.

    Returns a GoogleAuthState whose ``oauth_url`` should be opened in the
    browser.  Block on ``state.done`` and then read ``state.result``.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    redirect_uri = f"http://127.0.0.1:{port}"
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        })
    )

    state = GoogleAuthState(oauth_url=oauth_url, port=port)
    _start_callback_server(state, redirect_uri)
    return state


_PAGES_URL = "https://hiba-chaabnia.github.io/LeetVibe/"


def _start_callback_server(state: GoogleAuthState, redirect_uri: str) -> None:
    """Spin up a one-shot HTTP server in a daemon thread to catch the OAuth redirect."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            params = dict(urllib.parse.parse_qsl(
                urllib.parse.urlparse(self.path).query
            ))
            _resolve(state, params, redirect_uri)
            location = _PAGES_URL + ("?auth=done" if state.result and state.result.ok else "?auth=error")
            self.send_response(302)
            self.send_header("Location", location)
            self.end_headers()

        def log_message(self, *_):
            pass

    server = http.server.HTTPServer(("127.0.0.1", state.port), _Handler)

    def _serve():
        while not state.done.is_set():
            server.handle_request()
        server.server_close()

    threading.Thread(target=_serve, daemon=True).start()


def _resolve(state: GoogleAuthState, params: dict, redirect_uri: str) -> None:
    """Called from the HTTP handler thread once the callback params arrive."""
    if "error" in params:
        state.result = AuthResult(ok=False, error=params["error"])
        state.done.set()
        return

    code = params.get("code")
    if not code:
        state.result = AuthResult(ok=False, error="No authorization code received.")
        state.done.set()
        return

    try:
        # Exchange authorization code for Google tokens
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        token_data = token_resp.json()
        if "error" in token_data:
            state.result = AuthResult(ok=False, error=token_data.get("error_description", "Token exchange failed."))
            state.done.set()
            return

        google_id_token = token_data.get("id_token", "")

        # Sign into Firebase with the Google ID token
        fb_resp = requests.post(
            f"{_AUTH_BASE}:signInWithIdp",
            params={"key": FIREBASE_WEB_API_KEY},
            json={
                "requestUri": redirect_uri,
                "postBody": f"id_token={google_id_token}&providerId=google.com",
                "returnSecureToken": True,
                "returnIdpCredential": True,
            },
            timeout=10,
        )
        fb_data = fb_resp.json()
        if "error" in fb_data:
            state.result = AuthResult(ok=False, error=_friendly(fb_data["error"]))
        else:
            _save_session(fb_data)
            state.result = AuthResult(ok=True, user_id=fb_data["localId"], email=fb_data.get("email"))
    except Exception as exc:
        state.result = AuthResult(ok=False, error=str(exc)[:80])
    finally:
        state.done.set()


# ── Internals ─────────────────────────────────────────────────────────────────

def _save_session(data: dict) -> None:
    _SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SESSION_PATH.write_text(
        json.dumps({
            "id_token": data.get("idToken", ""),
            "refresh_token": data.get("refreshToken", ""),
            "user_id": data.get("localId", ""),
            "email": data.get("email", ""),
        }),
        encoding="utf-8",
    )


def _friendly(error: Any) -> str:
    """Convert a Firebase error response to a short user-readable string."""
    msg = error.get("message", "") if isinstance(error, dict) else str(error)
    if "EMAIL_EXISTS" in msg:
        return "An account with this email already exists."
    if "INVALID_PASSWORD" in msg or "INVALID_LOGIN_CREDENTIALS" in msg or "EMAIL_NOT_FOUND" in msg:
        return "Wrong email or password."
    if "WEAK_PASSWORD" in msg:
        return "Password must be at least 6 characters."
    if "TOO_MANY_ATTEMPTS" in msg or "TOO_MANY_REQUESTS" in msg:
        return "Too many attempts. Please wait and try again."
    if "INVALID_EMAIL" in msg:
        return "Invalid email address."
    if "network" in msg.lower():
        return "Network error. Check your connection and try again."
    return msg[:80]
