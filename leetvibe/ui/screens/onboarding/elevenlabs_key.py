"""ElevenLabsKeyScreen — optional ElevenLabs API key setup for voice narration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import set_key
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Input, Label, Static

from ...widgets import HintLabel
from ...widgets.shimmer_title import ShimmerTitle

_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"


class ElevenLabsKeyScreen(Screen[bool]):
    """Collects an ElevenLabs API key.

    During onboarding (``standalone=False``, the default) it's the last
    optional step before auth — skipping continues the chain. Pushed later
    from AI Settings (``standalone=True``) it just dismisses with whether a
    key was saved, same contract as ``ApiKeyScreen``.

    Shares ApiKeyScreen's CSS_PATH — see key_screens.tcss.
    """

    CSS_PATH = Path(__file__).parent / "key_screens.tcss"

    def __init__(self, standalone: bool = False, replacing: bool = False) -> None:
        super().__init__()
        self._standalone = standalone
        self._replacing = replacing

    def compose(self) -> ComposeResult:
        description = (
            "Enter a new [bold white]ElevenLabs API key[/bold white] to replace "
            "your current one."
            if self._replacing
            else
            "An [bold white]ElevenLabs API key[/bold white] is required to use voice.\n"
            "You can skip this step and voice features will be disabled."
        )
        with Static(id="api-container"):
            yield ShimmerTitle("ElevenLabs Voice (optional)", id="api-title")
            yield Static(description, id="api-description")
            yield Label(
                "Get your free key at "
                "[bold][@click=screen.open_url('https://elevenlabs.io')]elevenlabs.io[/][/bold] "
                "(10k chars/month)",
                id="link-hint",
            )
            yield Input(
                password=True,
                placeholder="Enter your ElevenLabs API Key",
                id="api-key-input",
            )
        with Horizontal(id="submit-hint-inline"):
            yield HintLabel("Enter", "save", self._submit_from_input)
            yield Label("·", classes="hint-sep")
            if self._standalone:
                yield HintLabel("Esc", "go back", self._go_back)
            else:
                yield HintLabel("Ctrl+J", "jump ahead", self._skip)
                yield Label("·", classes="hint-sep")
                yield HintLabel("Esc", "go back", self._go_back)

    def on_mount(self) -> None:
        self.query_one("#api-key-input", Input).focus()

    def action_open_url(self, url: str) -> None:
        self.app.open_url(url)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit(event.value)

    def _submit_from_input(self) -> None:
        self._submit(self.query_one("#api-key-input", Input).value)

    def on_key(self, event: Key) -> None:
        if event.key == "ctrl+j" and not self._standalone:
            self._skip()
        elif event.key == "escape":
            self._go_back()

    def _go_back(self) -> None:
        if self._standalone:
            self.dismiss(False)
        else:
            self.app.pop_screen()

    def _submit(self, raw: str) -> None:
        key = raw.strip()
        if not key:
            self._skip()
            return
        _LEETVIBE_HOME.mkdir(parents=True, exist_ok=True)
        set_key(str(_USER_ENV_PATH), "ELEVENLABS_API_KEY", key)
        os.environ["ELEVENLABS_API_KEY"] = key
        if self._standalone:
            self.dismiss(True)
        else:
            self._go_auth()

    def _skip(self) -> None:
        """Proceed without a key — voice narration will be silently disabled."""
        if self._standalone:
            self.dismiss(False)
        else:
            self._go_auth()

    def _go_auth(self) -> None:
        from ..auth import AuthChoiceScreen
        self.app.push_screen(AuthChoiceScreen(onboarding=True), self._finish)

    def _finish(self, result) -> None:
        """Auth flow done (signed in or skipped) — setup is complete."""
        self.app.exit("completed")
