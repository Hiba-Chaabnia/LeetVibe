"""Gradient ASCII banner widget for LeetVibe TUI."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

gradient = ["#FFD700", "#FFAF00", "#FF8205", "#FA500F", "#E92700"]

# Block-character ASCII art for "LEETVIBE"  (5 rows × 8 chars per letter, 1-space gap)
# ASCII art for LEETVIBE
ascii_lines = [
    "██      ███████ ███████ ████████ ██    ██ ██ ██████  ███████ ",
    "██      ██      ██         ██    ██    ██ ██ ██   ██ ██      ",
    "██      █████   █████      ██    ██    ██ ██ ██████  █████   ",
    "██      ██      ██         ██     ██  ██  ██ ██   ██ ██      ",
    "███████ ███████ ███████    ██      ████   ██ ██████  ███████ "
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
        n = len(ascii_lines)

        # Distribute gradient evenly across all 5 lines (one solid color per line)
        for i, line in enumerate(ascii_lines):
            idx = int(i * (len(gradient) - 1) / max(1, n - 1))
            banner.append(line + "\n", style=f"bold {gradient[idx]}")

        banner.append("\n")

        # Subtitle with character-level gradient
        subtitle = _chargradient(
            "⚡ AI Pair Programming for LeetCode  ·  Mistral AI Hackathon 2026 ⚡",
            gradient,
        )
        banner.append_text(subtitle)
        banner.append("\n")
        return banner
