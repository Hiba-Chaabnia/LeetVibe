"""AuthChoiceScreen — lets the user pick sign up, sign in, Google, or skip."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Static

_GRADIENT = ["#FFD700", "#FFAF00", "#FF8205", "#FA500F", "#E92700"]


def _gradient_text(text: str) -> Text:
    rich = Text(justify="center")
    n = len(text)
    for i, ch in enumerate(text):
        idx = int(i / max(1, n - 1) * (len(_GRADIENT) - 1))
        rich.append(ch, style=f"bold {_GRADIENT[idx]}")
    return rich


class AuthChoiceScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="auth-container"):
            yield Static("", id="auth-title")
            yield Static(
                "Create a free account to sync your solved problems across devices.",
                id="auth-subtitle",
            )
            yield Button("G  Continue with Google", id="btn-google", classes="auth-btn")
            yield Button("→  Sign In",              id="btn-login",  classes="auth-btn")
            yield Button("✦  Create Account",       id="btn-signup", classes="auth-btn")
            yield Static(
                "⚠  [bold #FFB300]Note:[/bold #FFB300] Google sign-in is recommended. "
                "Email sign-in is currently subject to rate limits.",
                id="auth-note",
            )
        yield Label(
            "[bold #FF8205]Tab[/bold #FF8205] to navigate  ·  "
            "[bold #FF8205]Enter[/bold #FF8205] to select  ·  "
            "[bold #FF8205]S[/bold #FF8205] to skip",
            id="auth-hint",
        )

    def on_mount(self) -> None:
        self.query_one("#auth-title", Static).update(
            _gradient_text("👤  Create or Sign In")
        )
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

    def on_key(self, event) -> None:
        if event.key in ("s", "escape"):
            self.app.exit("completed")
