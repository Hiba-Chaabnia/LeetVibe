"""WelcomeScreen — first onboarding step, shows banner and prompts Enter."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.widgets import Label

from ...widgets.banner import Banner


class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Banner(id="welcome-banner")
        yield Label(
            "[bold #FF8205]Enter[/bold #FF8205] to continue · "
            "[bold #FF8205]Esc[/bold #FF8205] to quit",
            id="hint",
        )

    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            from .api_key import ApiKeyScreen
            self.app.push_screen(ApiKeyScreen())
        elif event.key == "escape":
            self.app.exit(None)
