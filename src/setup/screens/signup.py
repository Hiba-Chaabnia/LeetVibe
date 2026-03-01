"""SignupScreen (onboarding) — email, password, and confirm during first-run setup."""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
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
            yield Label("Tab to switch fields  ·  Enter to create  ·  Esc to go back", id="form-hint")

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "enter":
            email = self.query_one("#email-input", Input).value
            password = self.query_one("#password-input", Input).value
            confirm = self.query_one("#confirm-input", Input).value
            self._submit(email, password, confirm)

    def _submit(self, email: str, password: str, confirm: str) -> None:
        email = email.strip()
        password = password.strip()
        confirm = confirm.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        if password != confirm:
            self.query_one("#form-error", Label).update("Passwords do not match.")
            return
        self._run_sign_up(email, password)

    @work
    async def _run_sign_up(self, email: str, password: str) -> None:
        from ...cloud.auth import sign_up
        self.query_one("#form-error", Label).update("Creating account…")
        result = await asyncio.to_thread(sign_up, email, password)
        if result.ok:
            self.app.exit("completed")
        else:
            self.query_one("#form-error", Label).update(result.error or "Sign up failed.")
