"""LoginScreen (onboarding) — email and password sign-in during first-run setup."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Input, Label, Static


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Sign In", id="form-title")
            yield Input(placeholder="Email", id="email-input", classes="form-input")
            yield Input(placeholder="Password", password=True, id="password-input", classes="form-input")
            yield Label("", id="form-error")
            yield Label(
                "[bold #FF8205]Tab[/bold #FF8205] to switch fields · "
                "[bold #FF8205]Enter[/bold #FF8205] to sign in ·\n "
                "[bold #FF8205]Esc[/bold #FF8205] to go back",
                id="form-hint",
            )

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "enter":
            email = self.query_one("#email-input", Input).value
            password = self.query_one("#password-input", Input).value
            self._submit(email, password)

    def _submit(self, email: str, password: str) -> None:
        email = email.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        self._run_sign_in(email, password)

    @work(thread=True)
    def _run_sign_in(self, email: str, password: str) -> None:
        from ...cloud.auth import sign_in
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
                self.app.exit("completed")
            else:
                self.query_one("#form-error", Label).update(result.error or "Sign in failed.")
                self.query_one("#email-input", Input).focus()
        except Exception:
            pass
