"""Gradient ASCII banner widget for LeetVibe TUI."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from ..theme import GRADIENT

# Block-character ASCII art for "LEETVIBE"  (5 rows × 8 chars per letter, 1-space gap)
_ASCII_LINES = [
    "██      ███████ ███████ ████████ ██    ██ ██ ██████  ███████ ",
    "██      ██      ██         ██    ██    ██ ██ ██   ██ ██      ",
    "██      █████   █████      ██    ██    ██ ██ ██████  █████   ",
    "██      ██      ██         ██     ██  ██  ██ ██   ██ ██      ",
    "███████ ███████ ███████    ██      ████   ██ ██████  ███████ ",
]

_SUBTITLE_LINES = [
    "Crack LeetCode with Mistral Vibe  ·  Mistral Global Hackathon 2026",
]


def _chargradient(text: str, colors: list[str]) -> Text:
    """Apply a character-level gradient across the given text."""
    rich_text = Text()
    n = len(text)
    for i, char in enumerate(text):
        idx = int(i / max(1, n - 1) * (len(colors) - 1))
        rich_text.append(char, style=f"bold {colors[idx]}")
    return rich_text


class Banner(Static):
    """Renders the LeetVibe block-char banner with fire gradient."""

    DEFAULT_CSS = """
    Banner {
        text-align: center;
        padding: 1 2;
        height: auto;
    }
    """

    def on_mount(self) -> None:
        self.update(self._render_banner())

    def _render_banner(self) -> Text:
        banner = Text(justify="center")
        n = len(_ASCII_LINES)

        # One solid gradient color per ASCII row
        for i, line in enumerate(_ASCII_LINES):
            idx = int(i * (len(GRADIENT) - 1) / max(1, n - 1))
            banner.append(line + "\n", style=f"bold {GRADIENT[idx]}")

        banner.append("\n")

        # Two-line subtitle, each line gets its own character-level gradient
        for line in _SUBTITLE_LINES:
            banner.append_text(_chargradient(line, GRADIENT))
            banner.append("\n")

        return banner
