"""LoginScreen (onboarding) — email and password sign-in during first-run setup."""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
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
                "[bold #FF8205]Tab[/bold #FF8205] to switch fields  ·  "
                "[bold #FF8205]Enter[/bold #FF8205] to sign in  ·  "
                "[bold #FF8205]Esc[/bold #FF8205] to go back",
                id="form-hint",
            )

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "enter":
            email = self.query_one("#email-input", Input).value
            password = self.query_one("#password-input", Input).value
            self._submit(email, password)

    def _submit(self, email: str, password: str) -> None:
        email = email.strip()
        password = password.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        self._run_sign_in(email, password)

    @work
    async def _run_sign_in(self, email: str, password: str) -> None:
        from ...cloud.auth import sign_in
        self.query_one("#form-error", Label).update("Signing in…")
        result = await asyncio.to_thread(sign_in, email, password)
        if result.ok:
            self.app.exit("completed")
        else:
            self.query_one("#form-error", Label).update(result.error or "Sign in failed.")
