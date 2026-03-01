"""AuthChoiceScreen — lets the user pick sign in, sign up, Google, or skip."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, OptionList, Static
from textual.widgets.option_list import Option


class AuthChoiceScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="auth-container"):
            yield Label(
                "Want to keep your progress?",
                id="auth-notice",
            )
            yield Label(
                "Creating a free account lets you sync your solved problems\n"
                "across devices and reinstalls. You can always do this later.",
                id="auth-detail",
            )
            yield OptionList(
                Option("→  Sign In        I already have an account", id="login"),
                Option("✦  Create Account  Start syncing my progress", id="signup"),
                Option("G  Google          Sign in with Google", id="google"),
                Option("✕  Skip            Continue without an account", id="skip"),
                id="auth-menu",
            )

    def on_mount(self) -> None:
        self.query_one("#auth-menu", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        oid = event.option.id
        if oid == "skip":
            self.app.exit("completed")
        elif oid == "login":
            from .login import LoginScreen
            self.app.push_screen(LoginScreen())
        elif oid == "signup":
            from .signup import SignupScreen
            self.app.push_screen(SignupScreen())
        elif oid == "google":
            from .google_auth import GoogleAuthScreen
            self.app.push_screen(GoogleAuthScreen())

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.exit("completed")
