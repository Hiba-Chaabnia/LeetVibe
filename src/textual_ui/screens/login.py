"""LoginScreen — email/password and Google OAuth sign-in / sign-up."""

from __future__ import annotations

import webbrowser

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Static

from ..theme import DIM, FIRE, GREEN, RED
from .base import BaseScreen


class LoginScreen(BaseScreen):
    """Sign in / sign up with email+password or Google OAuth."""

    BINDINGS = [
        Binding("escape", "dismiss_screen", "← Back"),
    ]

    DEFAULT_CSS = f"""
    LoginScreen {{
        align: center middle;
    }}
    #login-container {{
        width: 58;
        height: auto;
        border: round {FIRE};
        background: #0e0e0e;
        padding: 1 2 2 2;
    }}
    #login-title {{
        width: 100%;
        content-align: center middle;
        color: {FIRE};
        text-style: bold;
        margin: 0 0 1 0;
        height: 1;
    }}
    #mode-row {{
        height: 3;
        width: 100%;
        align: center middle;
        margin: 0 0 1 0;
    }}
    #btn-signin-mode, #btn-signup-mode {{
        border: tall #444444;
        background: transparent;
        color: {DIM};
        padding: 0 2;
        min-width: 12;
        height: 3;
    }}
    #btn-signin-mode.active {{
        background: #3a2200;
        color: {FIRE};
        text-style: bold;
        border: tall {FIRE};
    }}
    #btn-signup-mode.active {{
        background: #3a2200;
        color: {FIRE};
        text-style: bold;
        border: tall {FIRE};
    }}
    #login-status {{
        width: 100%;
        color: {DIM};
        height: 1;
        text-align: center;
        margin: 0 0 1 0;
    }}
    #btn-submit {{
        width: 100%;
        margin: 1 0 0 0;
        background: {FIRE};
        color: #000000;
        text-style: bold;
        border: none;
        height: 3;
    }}
    #btn-submit:hover {{ background: #FFB300; }}
    #btn-submit:disabled {{ background: #3a2200; color: #555555; }}
    #divider {{
        width: 100%;
        content-align: center middle;
        color: {DIM};
        margin: 1 0;
        height: 1;
    }}
    #btn-google {{
        width: 100%;
        border: tall #444444;
        background: transparent;
        color: #e0e0e0;
        height: 3;
    }}
    #btn-google:hover {{ background: #1a1a1a; border: tall #888888; }}
    #btn-google:disabled {{ color: #444444; border: tall #2a2a2a; }}
    #login-error {{
        width: 100%;
        color: {RED};
        height: auto;
        min-height: 1;
        margin: 1 0 0 0;
        text-align: center;
    }}
    #login-info {{
        width: 100%;
        color: {GREEN};
        height: auto;
        min-height: 1;
        margin: 0;
        text-align: center;
    }}
    """

    def __init__(self) -> None:
        super().__init__()
        self._mode = "signin"
        self._busy = False

    def compose(self) -> ComposeResult:
        with Container(id="login-container"):
            yield Static("🔐  LeetVibe Account", id="login-title")
            with Horizontal(id="mode-row"):
                yield Button("Sign In", id="btn-signin-mode", classes="active")
                yield Button("Sign Up", id="btn-signup-mode")
            yield Static("", id="login-status")
            yield Input(placeholder="Email", id="email-input")
            yield Input(placeholder="Password", password=True, id="password-input")
            yield Button("Sign In", id="btn-submit")
            yield Static("─────────── or ───────────", id="divider")
            yield Button("● Sign in with Google", id="btn-google")
            yield Static("", id="login-error")
            yield Static("", id="login-info")

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    # ── Mode toggle ──────────────────────────────────────────────────

    def _switch_mode(self, mode: str) -> None:
        self._mode = mode
        label = "Sign In" if mode == "signin" else "Sign Up"
        self.query_one("#btn-submit", Button).label = label
        sin = self.query_one("#btn-signin-mode", Button)
        sup = self.query_one("#btn-signup-mode", Button)
        if mode == "signin":
            sin.add_class("active")
            sup.remove_class("active")
        else:
            sin.remove_class("active")
            sup.add_class("active")
        self._clear_messages()

    def _clear_messages(self) -> None:
        self.query_one("#login-error", Static).update("")
        self.query_one("#login-info", Static).update("")

    # ── Busy state ───────────────────────────────────────────────────

    def _set_busy(self, busy: bool, status: str = "") -> None:
        self._busy = busy
        self.query_one("#btn-submit", Button).disabled = busy
        self.query_one("#btn-google", Button).disabled = busy
        self.query_one("#email-input", Input).disabled = busy
        self.query_one("#password-input", Input).disabled = busy
        self.query_one("#login-status", Static).update(status)

    def _update_login_status(self, msg: str) -> None:
        """Thread-safe status update (called via call_from_thread)."""
        self.query_one("#login-status", Static).update(msg)

    # ── Events ───────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-signin-mode":
            self._switch_mode("signin")
        elif btn_id == "btn-signup-mode":
            self._switch_mode("signup")
        elif btn_id == "btn-submit":
            self._submit_email_auth()
        elif btn_id == "btn-google":
            self._set_busy(True, "Opening browser…")
            self._run_google_auth()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "email-input":
            self.query_one("#password-input", Input).focus()
        elif event.input.id == "password-input":
            self._submit_email_auth()

    # ── Email auth ───────────────────────────────────────────────────

    def _submit_email_auth(self) -> None:
        if self._busy:
            return
        email = self.query_one("#email-input", Input).value.strip()
        password = self.query_one("#password-input", Input).value
        if not email or not password:
            self.query_one("#login-error", Static).update("Enter your email and password.")
            return
        status = "Signing in…" if self._mode == "signin" else "Creating account…"
        self._set_busy(True, status)
        self._run_email_auth(email, password, self._mode)

    @work(thread=True)
    def _run_email_auth(self, email: str, password: str, mode: str) -> None:
        from ...cloud.auth import sign_in, sign_up
        result = sign_in(email, password) if mode == "signin" else sign_up(email, password)
        self.app.call_from_thread(self._on_auth_result, result)

    # ── Google OAuth ─────────────────────────────────────────────────

    @work(thread=True)
    def _run_google_auth(self) -> None:
        from ...cloud.auth import AuthResult, start_google_auth
        state = start_google_auth()
        if isinstance(state, AuthResult):
            self.app.call_from_thread(self._on_auth_result, state)
            return
        webbrowser.open(state.oauth_url)
        self.app.call_from_thread(self._update_login_status, "Waiting for Google sign-in…")
        state.done.wait(timeout=120)
        result = state.result or AuthResult(ok=False, error="Timed out. Try again.")
        self.app.call_from_thread(self._on_auth_result, result)

    # ── Result handler ───────────────────────────────────────────────

    def _on_auth_result(self, result) -> None:
        """Called on the main thread once auth completes."""
        try:
            self._set_busy(False)
        except Exception:
            return  # screen was dismissed before the worker finished
        if result.ok:
            self.dismiss(result)
        else:
            self.query_one("#login-error", Static).update(
                result.error or "Authentication failed."
            )

    def action_dismiss_screen(self) -> None:
        self.dismiss(None)
