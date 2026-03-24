"""Shared utilities for onboarding screens."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ...theme import SHIMMER as _SHIMMER


class ShimmerTitle(Static):
    """A title widget that animates with the brand fire shimmer effect."""

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__("", markup=False, **kwargs)
        self._text = text
        self._offset = 0

    def on_mount(self) -> None:
        self._redraw()
        self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        self._offset = (self._offset + 1) % len(_SHIMMER)
        self._redraw()

    def _redraw(self) -> None:
        n = len(_SHIMMER)
        rich = Text(justify="center")
        for i, ch in enumerate(self._text):
            color = _SHIMMER[(self._offset + i) % n]
            rich.append(ch, style=f"bold {color}")
        self.update(rich)
