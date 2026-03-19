"""ElevenLabsKeyScreen — optional ElevenLabs API key setup for voice narration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import set_key
from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Input, Label, Static

from ._utils import ShimmerTitle

_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"


class ElevenLabsKeyScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="api-container"):
            yield ShimmerTitle("ElevenLabs Voice  (optional)", id="api-title")
            yield Static(
                "LeetVibe can [bold white]narrate algorithm explanations[/bold white] "
                "aloud using [bold white]ElevenLabs[/bold white] text-to-speech.\n\n"
                "An [bold white]ElevenLabs API key[/bold white] is required to use voice. "
                "You can skip this step and voice features will be disabled.",
                id="api-description",
            )
            yield Label(
                "Get your free key at [bold]elevenlabs.io[/bold] (10k chars/month free)",
                id="link-hint",
            )
            yield Input(
                password=True,
                placeholder="Enter your ElevenLabs API Key",
                id="api-key-input",
            )
        yield Label(
            "[bold #FF8205]Enter[/bold #FF8205] to save  ·  "
            "[bold #FF8205]Tab[/bold #FF8205] to skip voice  ·  "
            "[bold #FF8205]Esc[/bold #FF8205] to cancel",
            id="submit-hint",
        )

    def on_mount(self) -> None:
        self.query_one("#api-key-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit(event.value)

    def on_key(self, event: Key) -> None:
        if event.key == "tab":
            self._skip()
        elif event.key == "escape":
            self.app.exit(None)

    def _submit(self, raw: str) -> None:
        key = raw.strip()
        if not key:
            self._skip()
            return
        _LEETVIBE_HOME.mkdir(parents=True, exist_ok=True)
        set_key(str(_USER_ENV_PATH), "ELEVENLABS_API_KEY", key)
        os.environ["ELEVENLABS_API_KEY"] = key
        from .auth_choice import AuthChoiceScreen
        self.app.push_screen(AuthChoiceScreen())

    def _skip(self) -> None:
        """Proceed without a key — voice narration will be silently disabled."""
        from .auth_choice import AuthChoiceScreen
        self.app.push_screen(AuthChoiceScreen())
