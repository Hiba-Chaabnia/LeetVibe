"""WelcomeScreen — first onboarding step, shows banner and prompts Enter."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Label

from ...widgets import HintLabel
from ...widgets.banner import Banner


class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Banner(id="welcome-banner")
        with Horizontal(id="hint"):
            yield HintLabel("Enter", "start setup", self._start_setup)
            yield Label("·", classes="hint-sep")
            yield HintLabel("Ctrl+Q", "quit", self._quit)

    def _start_setup(self) -> None:
        from .api_key import ApiKeyScreen
        self.app.push_screen(ApiKeyScreen())

    def _quit(self) -> None:
        self.app.exit(None)

    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            self._start_setup()
        elif event.key == "ctrl+q":
            self._quit()
