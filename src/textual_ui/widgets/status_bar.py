"""Bottom status bar widget."""

from __future__ import annotations

from collections.abc import Callable

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Click
from textual.widgets import Label, Static

# Hint tuple: (key_display, description, on_click_callback | None)
Hint = tuple[str, str, Callable[[], None] | None]


class HintLabel(Static):
    """A single clickable key-hint rendered as Rich text at height 1."""

    def __init__(
        self,
        key: str,
        desc: str,
        callback: Callable[[], None] | None,
        **kwargs,
    ) -> None:
        text = Text()
        text.append(key, style="bold #FF8205")
        text.append(f"  {desc}", style="#888888")
        super().__init__(text, **kwargs)
        self._callback = callback

    def on_click(self, event: Click) -> None:
        if self._callback is not None:
            event.stop()
            self._callback()


class StatusBar(Horizontal):
    """Bottom bar with clickable key hints, optional challenge count, and version.

    Layout modes
    ─────────────
    hints_centered=False (default)
        [hints (auto)]  [spacer (1fr)]  [version (auto)]

    hints_centered=True  (absolute screen centre)
        [count (1fr, left)]  [hints (auto)]  [version (1fr, right-aligned)]
    """

    ALLOW_MAXIMIZE = False

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: #16213e;
        padding: 0 2;
        dock: bottom;
    }
    StatusBar Label {
        color: #888888;
    }

    /* Hint container */
    StatusBar #status-hints {
        width: auto;
        height: 1;
        padding: 0;
    }

    /* Individual hint labels */
    HintLabel {
        height: 1;
        width: auto;
        padding: 0 1;
        background: transparent;
    }
    HintLabel:hover {
        background: #2a2a2a;
    }

    /* Default (left-aligned) layout */
    StatusBar #status-spacer { width: 1fr; }
    StatusBar #status-right  { width: auto; }

    /* Centred layout: count left — hints centre — version right */
    StatusBar.hints-centered #status-count { width: 1fr; }
    StatusBar.hints-centered #status-right { width: 1fr; text-align: right; }
    """

    def __init__(
        self,
        hints: list[Hint] | None = None,
        show_count: bool = False,
        hints_centered: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._hints = hints or []
        self._show_count = show_count
        self._hints_centered = hints_centered
        self._count = 0
        self._total = 0

    def on_mount(self) -> None:
        if self._hints_centered:
            self.add_class("hints-centered")

    def compose(self) -> ComposeResult:
        if self._hints_centered:
            # [count 1fr] [hints auto] [version 1fr right]
            yield Label(self._count_text() if self._show_count else "", id="status-count")
            with Horizontal(id="status-hints"):
                for i, (key, desc, cb) in enumerate(self._hints):
                    yield HintLabel(key, desc, cb, id=f"hint-{i}")
            yield Label("LeetVibe v0.1.0", id="status-right")
        else:
            # [hints auto] [spacer 1fr] [version auto]
            with Horizontal(id="status-hints"):
                for i, (key, desc, cb) in enumerate(self._hints):
                    yield HintLabel(key, desc, cb, id=f"hint-{i}")
            yield Label("", id="status-spacer")
            yield Label("LeetVibe v0.1.0", id="status-right")

    # ── Count helpers ──────────────────────────────────────────────────

    def _count_text(self) -> str:
        if self._total == 0:
            return "Loading…"
        if self._count == self._total:
            return f"{self._total:,} problems"
        return f"{self._count:,} / {self._total:,} problems"

    def update_count(self, count: int, total: int) -> None:
        self._count = count
        self._total = total
        if self._show_count:
            try:
                self.query_one("#status-count", Label).update(self._count_text())
            except Exception:
                pass
