"""ApiKeyScreen — collects, validates, and saves the Mistral API key."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import set_key
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Input, Label, Static  # Static used as container

from ...widgets import HintLabel
from ...widgets.shimmer_title import ShimmerTitle

_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"


def _verify_key(key: str) -> str | None:
    """Return None if the key is valid, or an error string if not.

    Uses models.list() — the cheapest possible Mistral API call (no tokens).
    """
    try:
        from mistralai import Mistral
        Mistral(api_key=key).models.list()
        return None
    except Exception as exc:
        msg = str(exc)
        if "401" in msg or "Unauthorized" in msg or "invalid_api_key" in msg.lower():
            return "Invalid API key. Check it and try again."
        if "403" in msg or "Forbidden" in msg:
            return "API key does not have the required permissions."
        if "network" in msg.lower() or "connection" in msg.lower():
            return "Network error. Check your connection and try again."
        return f"Could not verify key: {msg[:60]}"


class ApiKeyScreen(Screen[bool]):
    """Collects a Mistral API key.

    Used in two contexts: during onboarding (``standalone=False``, the
    default) it's one step in a chain — skip is allowed, and success moves
    on to ElevenLabs setup. Pushed later to unlock an AI mode from the home
    menu (``standalone=True``), there's no skip (the user already asked for
    AI) and it just dismisses with whether a key was saved.

    Uses its own CSS_PATH (rather than relying on the onboarding app's
    stylesheet) so it renders correctly when pushed onto the main app too —
    see key_screens.tcss.
    """

    CSS_PATH = Path(__file__).parent / "key_screens.tcss"

    def __init__(self, standalone: bool = False, replacing: bool = False) -> None:
        super().__init__()
        self._standalone = standalone
        self._replacing = replacing

    def compose(self) -> ComposeResult:
        if self._replacing:
            description = (
                "LeetVibe is powered by [bold white]Mistral AI[/bold white]\n\n"
                "Enter a new [bold white]Mistral API key[/bold white] to replace "
                "your current one."
            )
        elif self._standalone:
            description = (
                "LeetVibe is powered by [bold white]Mistral AI[/bold white]\n\n"
                "A [bold white]Mistral API key[/bold white] unlocks Learn, Pair "
                "Programming and Interview mode."
            )
        else:
            description = (
                "LeetVibe is powered by [bold white]Mistral AI[/bold white]\n\n"
                "A [bold white]Mistral API key[/bold white] unlocks Learn, Pair "
                "Programming and Interview mode.\n\n"
                "[bold white]No key?[/bold white] You can still use Practice mode — "
                "add a key anytime later from AI Settings."
            )
        with Static(id="api-container"):
            yield ShimmerTitle("Mistral API Key", id="api-title")
            yield Static(description, id="api-description")
            yield Label(
                "Get your key at "
                "[bold][@click=screen.open_url('https://console.mistral.ai')]console.mistral.ai[/][/bold]",
                id="link-hint",
            )
            yield Input(
                password=True,
                placeholder="Enter your Mistral API Key",
                id="api-key-input",
            )
            yield Label("", id="error-label")
        with Horizontal(id="submit-hint-inline"):
            yield HintLabel("Enter", "save", self._submit_from_input)
            if not self._standalone:
                yield Label("·", classes="hint-sep")
                yield HintLabel("Ctrl+J", "skip for now", self._skip)
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
        if event.key == "escape":
            self._go_back()
        elif event.key == "ctrl+j" and not self._standalone:
            self._skip()

    def _go_back(self) -> None:
        if self._standalone:
            self.dismiss(False)
        else:
            self.app.pop_screen()

    def _skip(self) -> None:
        """Onboarding only — proceed without a key, straight past ElevenLabs
        setup (voice narration is moot without AI sessions) to auth."""
        from ..auth import AuthChoiceScreen
        self.app.push_screen(AuthChoiceScreen(onboarding=True), self._finish)

    def _finish(self, result) -> None:
        self.app.exit("completed")

    def _submit(self, raw: str) -> None:
        key = raw.strip()
        if not key:
            self.query_one("#error-label", Label).update("Key cannot be empty.")
            return
        self._set_busy(True, "Verifying key…")
        self._run_verify(key)

    def _set_busy(self, busy: bool, status: str = "") -> None:
        inp = self.query_one("#api-key-input", Input)
        inp.disabled = busy
        self.query_one("#error-label", Label).update(
            f"[dim]{status}[/dim]" if busy else status
        )

    @work(thread=True)
    def _run_verify(self, key: str) -> None:
        error = _verify_key(key)
        self.app.call_from_thread(self._on_verify_result, key, error)

    def _on_verify_result(self, key: str, error: str | None) -> None:
        if error:
            self._set_busy(False)
            self.query_one("#error-label", Label).update(f"[bold #E53935]{error}[/]")
            self.query_one("#api-key-input", Input).focus()
            return

        # Key is valid — persist and proceed
        _LEETVIBE_HOME.mkdir(parents=True, exist_ok=True)
        set_key(str(_USER_ENV_PATH), "MISTRAL_API_KEY", key)
        os.environ["MISTRAL_API_KEY"] = key

        if self._standalone:
            self.dismiss(True)
        else:
            from .elevenlabs_key import ElevenLabsKeyScreen
            self.app.push_screen(ElevenLabsKeyScreen())
