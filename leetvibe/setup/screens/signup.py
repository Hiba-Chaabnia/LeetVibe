"""SignupScreen (onboarding) — email, password, and confirm during first-run setup."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Input, Label, Static


class SignupScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Create Account", id="form-title")
            yield Input(placeholder="Email", id="email-input", classes="form-input")
            yield Input(placeholder="Password", password=True, id="password-input", classes="form-input")
            yield Input(placeholder="Confirm password", password=True, id="confirm-input", classes="form-input")
            yield Label("", id="form-error")
            yield Label(
                "[bold #FF8205]Tab[/bold #FF8205] to switch fields · "
                "[bold #FF8205]Enter[/bold #FF8205] to create ·\n"
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
            confirm = self.query_one("#confirm-input", Input).value
            self._submit(email, password, confirm)

    def _submit(self, email: str, password: str, confirm: str) -> None:
        email = email.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        if password != confirm:
            self.query_one("#form-error", Label).update("Passwords do not match.")
            return
        self._run_sign_up(email, password)

    @work(thread=True)
    def _run_sign_up(self, email: str, password: str) -> None:
        from ...cloud.auth import sign_up
        self.app.call_from_thread(self._set_status, "Creating account…")
        result = sign_up(email, password)
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
                self.query_one("#form-error", Label).update(result.error or "Sign up failed.")
                self.query_one("#email-input", Input).focus()
        except Exception:
            pass
