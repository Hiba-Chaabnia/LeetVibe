"""ElevenLabsKeyScreen — optional ElevenLabs API key setup for voice narration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import set_key
from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, Static

_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"

_GRADIENT = ["#FFD700", "#FFAF00", "#FF8205", "#FA500F", "#E92700"]


def _gradient_text(text: str) -> Text:
    rich = Text(justify="center")
    n = len(text)
    for i, ch in enumerate(text):
        idx = int(i / max(1, n - 1) * (len(_GRADIENT) - 1))
        rich.append(ch, style=f"bold {_GRADIENT[idx]}")
    return rich



class ElevenLabsKeyScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="api-container"):
            yield Static("", id="api-title")
            yield Static(
                "LeetVibe can [bold white]narrate algorithm explanations[/bold white] "
                "aloud using [bold #FF8205]ElevenLabs[/bold #FF8205] text-to-speech.\n\n"
                "An [bold white]ElevenLabs API key[/bold white] is required to use voice. "
                "You can skip this step and voice features will be disabled.",
                id="api-description",
            )
            yield Label(
                "Get your free key at [bold]elevenlabs.io[/bold]  ·  10k chars/month free",
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
        self.query_one("#api-title", Static).update(
            _gradient_text("ElevenLabs Voice  (optional)")
        )
        self.query_one("#api-key-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit(event.value)

    def on_key(self, event) -> None:
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
