"""Bottom status bar widget."""

from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import version as _pkg_version, PackageNotFoundError

try:
    _VERSION = _pkg_version("leetvibe")
except PackageNotFoundError:
    _VERSION = "dev"

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Click
from textual.widgets import Label, Static

from ..theme import SHIMMER as _SHIMMER_COLORS

# Hint tuple: (key_display, description, on_click_callback | None[, gradient: bool])
Hint = tuple[str, str, Callable[[], None] | None] | tuple[str, str, Callable[[], None] | None, bool]


class HintLabel(Static):
    """A single clickable key-hint rendered as Rich text at height 1."""

    def __init__(
        self,
        key: str,
        desc: str,
        callback: Callable[[], None] | None,
        gradient: bool = False,
        **kwargs,
    ) -> None:
        self._key = key
        self._desc = desc
        self._callback = callback
        self._gradient = gradient
        self._offset = 0
        super().__init__(self._build_text(), **kwargs)

    def _build_text(self) -> Text:
        text = Text()
        text.append(self._key, style="bold #FF8205")
        if self._gradient:
            text.append("  ")
            full = f"to {self._desc}"
            n = len(_SHIMMER_COLORS)
            for i, char in enumerate(full):
                color = _SHIMMER_COLORS[(i + self._offset) % n]
                text.append(char, style=f"bold {color}")
        else:
            text.append(f"  to {self._desc}", style="#888888")
        return text

    def on_mount(self) -> None:
        if self._gradient:
            self.set_interval(0.08, self._shimmer)

    def _shimmer(self) -> None:
        self._offset = (self._offset + 1) % len(_SHIMMER_COLORS)
        self.update(self._build_text())

    def on_click(self, event: Click) -> None:
        if self._callback is not None:
            event.stop()
            self._callback()


class StatusBar(Horizontal):
    """Bottom bar with clickable key hints, optional problem count, and version.

    Layout modes
    ─────────────
    hints_centered=False (default)
        [hints (auto)]  [spacer (1fr)]  [version (auto)]

    hints_centered=True  (absolute screen centre)
        [count (1fr, left)]  [hints (auto)]  [version (1fr, right-aligned)]
    """

    ALLOW_MAXIMIZE = False

    def __init__(
        self,
        hints: list[Hint] | None = None,
        show_count: bool = False,
        hints_centered: bool = False,
        left_label: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._hints = hints or []
        self._show_count = show_count
        self._hints_centered = hints_centered
        self._left_label = left_label
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
                for i, hint in enumerate(self._hints):
                    if i > 0:
                        yield Label("·", id=f"sep-{i}", classes="hint-sep")
                    yield HintLabel(hint[0], hint[1], hint[2], gradient=len(hint) > 3 and bool(hint[3]), id=f"hint-{i}")
            yield Label(f"LeetVibe v{_VERSION}", id="status-right")
        elif self._left_label or not self._hints:
            # [left-label 1fr] [hints auto] [version auto]
            yield Label(self._left_label, id="status-left")
            with Horizontal(id="status-hints"):
                for i, hint in enumerate(self._hints):
                    if i > 0:
                        yield Label("·", id=f"sep-{i}", classes="hint-sep")
                    yield HintLabel(hint[0], hint[1], hint[2], gradient=len(hint) > 3 and bool(hint[3]), id=f"hint-{i}")
            yield Label(f"LeetVibe v{_VERSION}", id="status-right")
        else:
            # [hints auto] [spacer 1fr] [version auto]
            with Horizontal(id="status-hints"):
                for i, hint in enumerate(self._hints):
                    if i > 0:
                        yield Label("·", id=f"sep-{i}", classes="hint-sep")
                    yield HintLabel(hint[0], hint[1], hint[2], gradient=len(hint) > 3 and bool(hint[3]), id=f"hint-{i}")
            yield Label("", id="status-spacer")
            yield Label(f"LeetVibe v{_VERSION}", id="status-right")

    def update_left_label(self, text: str) -> None:
        """Update the left-side label text (e.g. auth status)."""
        try:
            self.query_one("#status-left", Label).update(text)
        except Exception:
            pass

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

    def set_hint_visible(self, index: int, visible: bool) -> None:
        """Show or hide a hint by index, then recompute all separator visibility."""
        try:
            self.query_one(f"#hint-{index}").display = visible
        except Exception:
            pass
        self._refresh_separators()

    def _refresh_separators(self) -> None:
        """Ensure no leading separator: sep-i is shown only when hint-i is visible
        and at least one hint at an earlier index is also visible."""
        first_visible_seen = False
        for i in range(len(self._hints)):
            try:
                hint_visible = self.query_one(f"#hint-{i}").display
            except Exception:
                hint_visible = False
            if i > 0:
                try:
                    self.query_one(f"#sep-{i}").display = hint_visible and first_visible_seen
                except Exception:
                    pass
            if hint_visible:
                first_visible_seen = True
