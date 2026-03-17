"""BaseScreen — shared actions and helpers for all LeetVibe screens."""

from __future__ import annotations

from typing import TypeVar

from textual.screen import Screen
from textual.widget import Widget

_W = TypeVar("_W", bound=Widget)


class BaseScreen(Screen):
    """Mixin base for every LeetVibe screen.

    Provides:
    - ``action_pop_screen``  — go back one screen
    - ``action_quit_app``    — exit the application
    - ``safe_query_one``     — query_one that returns None on miss instead of raising
    """

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def safe_query_one(self, selector: str, widget_type: type[_W]) -> _W | None:
        """Return the first widget matching *selector*, or ``None`` if not found."""
        try:
            return self.query_one(selector, widget_type)
        except Exception:
            return None
