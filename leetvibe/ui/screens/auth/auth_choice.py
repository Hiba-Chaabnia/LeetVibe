"""AuthChoiceScreen — lets the user pick sign up, sign in, Google, or skip.

Dismisses with the child screen's ``AuthResult`` once signed in, or ``None``
when the user skips / backs out.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.widgets import Button, Label, Static

from ...widgets import HintLabel
from ...widgets.shimmer_title import ShimmerTitle
from .base import AuthScreenBase


class AuthChoiceScreen(AuthScreenBase):
    def __init__(self, onboarding: bool = False) -> None:
        super().__init__()
        self._onboarding = onboarding

    def compose(self) -> ComposeResult:
        with Static(id="auth-container"):
            yield ShimmerTitle("Save Your Progress", id="auth-title")
            yield Static(
                "Create a free account to sync your solved problems across devices.",
                id="auth-subtitle",
            )
            yield Button("Continue with Google", id="btn-google", classes="auth-btn")
            with Horizontal(id="auth-row"):
                yield Button("Sign In",        id="btn-login",  classes="auth-btn")
                yield Button("Create Account", id="btn-signup", classes="auth-btn")

        with Horizontal(id="auth-hint"):
            yield HintLabel("Enter", "select", None)
            yield Label("·", classes="hint-sep")
            yield HintLabel("Tab", "navigate", None)
            if self._onboarding:
                yield Label("·", classes="hint-sep")
                yield HintLabel("Ctrl+J", "jump ahead", self._skip)

    def on_mount(self) -> None:
        self.query_one("#btn-google", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-signup":
            from .signup import SignupScreen
            self.app.push_screen(SignupScreen(), self._on_child_result)
        elif bid == "btn-login":
            from .login import LoginScreen
            self.app.push_screen(LoginScreen(), self._on_child_result)
        elif bid == "btn-google":
            from .google_auth import GoogleAuthScreen
            self.app.push_screen(GoogleAuthScreen(), self._on_child_result)

    def _on_child_result(self, result) -> None:
        """Signed in on a child screen — finish the whole flow with that result."""
        if result is not None and result.ok:
            self.dismiss(result)

    def _skip(self) -> None:
        self.dismiss(None)

    def on_key(self, event: Key) -> None:
        if event.key == "escape" or (self._onboarding and event.key == "ctrl+j"):
            self._skip()
