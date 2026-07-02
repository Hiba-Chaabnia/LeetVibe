"""Shared chat widgets — bubble transcript log and animated thinking indicator."""

from __future__ import annotations

from typing import Callable

from rich.panel import Panel
from rich.text import Text

from textual.widgets import RichLog, Static

from leetvibe.ui.markup import MARKUP_RE, esc
from leetvibe.ui.theme import AMBER, FIRE, GOLD, RED, SHIMMER

_SPINNER_FRAMES: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ThinkingIndicator(Static):
    """Animated spinner + shimmering label ("thinking…" by default)."""

    def __init__(self, label: str = "thinking…", **kwargs) -> None:
        super().__init__("", **kwargs)
        self._label = label
        self._offset: int = 0
        self._frame: int = 0

    def set_label(self, label: str) -> None:
        self._label = label
        if self.display:
            self.update(self._build_text())

    def on_mount(self) -> None:
        self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        if not self.display:
            return
        self._offset = (self._offset + 1) % len(SHIMMER)
        self._frame = (self._frame + 1) % len(_SPINNER_FRAMES)
        self.update(self._build_text())

    def _build_text(self) -> Text:
        text = Text()
        text.append("  ")
        text.append(_SPINNER_FRAMES[self._frame], style=f"bold {FIRE}")
        text.append(" ")
        for i, ch in enumerate(self._label):
            color = SHIMMER[(i + self._offset) % len(SHIMMER)]
            text.append(ch, style=f"bold {color}")
        return text


class ChatBubbleLog(RichLog):
    """RichLog that renders conversation turns as titled bubble panels.

    ``renderer`` converts raw AI content (markdown, possibly with Rich markup)
    to a Rich markup string before display; user content is always escaped.
    """

    def __init__(
        self,
        *args,
        renderer: Callable[[str], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._renderer = renderer

    # ── Internals ─────────────────────────────────────────────────────

    def _render_content(self, content: str) -> Text:
        markup = self._renderer(content) if self._renderer else esc(content)
        try:
            return Text.from_markup(markup)
        except Exception:
            # Malformed markup (stray brackets from the model) — show plain text
            return Text(MARKUP_RE.sub("", markup))

    def _write_panel(self, body, title: str, border: str) -> None:
        # expand=True on write: bubbles always span the log's full width
        # (RichLog otherwise sizes each renderable to its content).
        self.write(
            Panel(
                body,
                title=title,
                title_align="left",
                border_style=border,
                padding=(0, 1),
                expand=True,
            ),
            expand=True,
        )
        self.scroll_end(animate=False)

    # ── Bubbles ───────────────────────────────────────────────────────

    def append_user(self, message: str, speaker: str = "you") -> None:
        self._write_panel(
            esc(message), f"[bold {AMBER}] {speaker} [/bold {AMBER}]", AMBER
        )

    def append_ai(self, content: str, speaker: str = "vibe") -> None:
        self._write_panel(
            self._render_content(content),
            f"[bold {FIRE}] {speaker} [/bold {FIRE}]",
            FIRE,
        )

    def append_mnemonic(self, text: str) -> None:
        self._write_panel(
            Text.from_markup(f"[italic]{esc(text)}[/italic]"),
            f"[bold {GOLD}] 💡 mnemonic [/bold {GOLD}]",
            GOLD,
        )

    def append_error(self, message: str) -> None:
        self._write_panel(
            f"[{RED}]{esc(message)}[/{RED}]",
            f"[bold {RED}] error [/bold {RED}]",
            RED,
        )

    def append_raw(self, line: str) -> None:
        self.write(line)
        self.scroll_end(animate=False)

    # ── History ───────────────────────────────────────────────────────

    def restore_history(self, messages: list[dict], ai_speaker: str = "vibe") -> None:
        """Clear the log and re-render a saved conversation as bubbles."""
        self.clear()
        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content") or "").strip()
            if not content:
                continue
            if role == "user":
                self.append_user(content)
            elif role == "assistant":
                self.append_ai(content, speaker=ai_speaker)
