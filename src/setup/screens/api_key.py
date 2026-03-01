"""ApiKeyScreen — collects and saves the Mistral API key."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import set_key
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, Static

_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"


class ApiKeyScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="api-container"):
            yield Label("Enter your Mistral API key to get started.", id="instruction")
            yield Label("Get one at: console.mistral.ai/codestral", id="link-hint")
            yield Input(password=True, placeholder="sk-...", id="api-key-input")
            yield Label("", id="error-label")
            yield Label("Enter to save  ·  Esc to cancel", id="submit-hint")

    def on_mount(self) -> None:
        self.query_one("#api-key-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save_key(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.exit(None)

    def _save_key(self, raw: str) -> None:
        key = raw.strip()
        if not key:
            self.query_one("#error-label", Label).update("Key cannot be empty.")
            return

        _LEETVIBE_HOME.mkdir(parents=True, exist_ok=True)
        set_key(str(_USER_ENV_PATH), "MISTRAL_API_KEY", key)
        os.environ["MISTRAL_API_KEY"] = key

        from .auth_choice import AuthChoiceScreen
        self.app.push_screen(AuthChoiceScreen())
