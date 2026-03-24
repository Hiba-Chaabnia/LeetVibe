"""AuthChoiceScreen — lets the user pick sign up, sign in, Google, or skip."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Button, Label, Static

from ._utils import ShimmerTitle


class AuthChoiceScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="auth-container"):
            yield ShimmerTitle("Create or Sign In", id="auth-title")
            yield Static(
                "Create a free account to sync your solved problems across devices.",
                id="auth-subtitle",
            )
            yield Button("G  Continue with Google", id="btn-google", classes="auth-btn")
            yield Button("→  Sign In",              id="btn-login",  classes="auth-btn")
            yield Button("✦  Create Account",       id="btn-signup", classes="auth-btn")

        yield Label(
            "[bold #FF8205]Tab[/bold #FF8205] to navigate · "
            "[bold #FF8205]Enter[/bold #FF8205] to select\n"
            "[bold #FF8205]S[/bold #FF8205] to skip",
            id="auth-hint",
        )

    def on_mount(self) -> None:
        self.query_one("#btn-google", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-signup":
            from .signup import SignupScreen
            self.app.push_screen(SignupScreen())
        elif bid == "btn-login":
            from .login import LoginScreen
            self.app.push_screen(LoginScreen())
        elif bid == "btn-google":
            from .google_auth import GoogleAuthScreen
            self.app.push_screen(GoogleAuthScreen())

    def on_key(self, event: Key) -> None:
        if event.key in ("s", "escape"):
            self.app.exit("completed")
