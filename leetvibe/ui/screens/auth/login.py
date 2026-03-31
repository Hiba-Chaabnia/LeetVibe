"""LoginScreen — email and password sign-in for the shared auth flow."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.widgets import Input, Label, Static

from ...widgets import HintLabel
from ...widgets.shimmer_title import ShimmerTitle
from .base import AuthScreenBase


class LoginScreen(AuthScreenBase):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield ShimmerTitle("Sign In", id="form-title")
            yield Static(
                "Welcome back — pick up where you left off.",
                id="form-subtitle",
            )
            yield Input(placeholder="Email", id="email-input", classes="form-input")
            yield Input(placeholder="Password", password=True, id="password-input", classes="form-input")
            yield Label("", id="form-error")
        with Horizontal(id="form-hint-inline"):
            yield HintLabel("Enter", "sign in", self._submit_from_inputs)
            yield Label("·", classes="hint-sep")
            yield HintLabel("Tab", "switch fields", None)
            yield Label("·", classes="hint-sep")
            yield HintLabel("Esc", "go back", self._go_back)

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def _go_back(self) -> None:
        self.dismiss(None)

    def _submit_from_inputs(self) -> None:
        email = self.query_one("#email-input", Input).value
        password = self.query_one("#password-input", Input).value
        self._submit(email, password)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self._go_back()
        elif event.key == "enter":
            self._submit_from_inputs()

    def _submit(self, email: str, password: str) -> None:
        email = email.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        self._run_sign_in(email, password)

    @work(thread=True)
    def _run_sign_in(self, email: str, password: str) -> None:
        from leetvibe.cloud.auth import sign_in
        self.app.call_from_thread(
            self._set_status, "Signing in…"
        )
        result = sign_in(email, password)
        self.app.call_from_thread(self._on_result, result)

    def _set_status(self, msg: str) -> None:
        try:
            self.query_one("#form-error", Label).update(msg)
        except Exception:
            pass

    def _on_result(self, result) -> None:
        try:
            if result.ok:
                self.dismiss(result)
            else:
                self.query_one("#form-error", Label).update(result.error or "Sign in failed.")
                self.query_one("#email-input", Input).focus()
        except Exception:
            pass
