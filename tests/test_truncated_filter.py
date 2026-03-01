"""
tests/test_truncated_filter.py
──────────────────────────────
Stand-alone Textual experiment: truncate Select filter labels when the
selected text is wider than the widget's visible area, replacing overflow
with "…".

Run with:
    python tests/test_truncated_filter.py
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Select, Static


# ── helpers ──────────────────────────────────────────────────────────────────


def _truncate(text: str, max_chars: int, ellipsis: str = "…") -> str:
    """Return *text* clipped to *max_chars*, appending *ellipsis* on overflow."""
    if len(text) <= max_chars:
        return text
    keep = max(0, max_chars - len(ellipsis))
    return text[:keep] + ellipsis


# ── widget ────────────────────────────────────────────────────────────────────


class TruncatedSelect(Select):
    """A Select widget that truncates the current label to fit its width.

    After each value change or resize the inner ``#label`` Static is updated
    with a string that fits the available character budget.
    """

    def __init__(self, options: list[tuple[str, str]], **kwargs) -> None:
        super().__init__(options, **kwargs)
        # Private lookup so we never need to poke at Textual internals.
        self._option_map: dict[str, str] = {str(val): label for label, val in options}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _label_for(self, value: object) -> str | None:
        """Return the display label for *value*, or ``None`` for BLANK."""
        if value is Select.BLANK:
            return None
        return self._option_map.get(str(value))

    def _apply_truncation(self) -> None:
        """Locate the inner ``#label`` Static and re-render it truncated."""
        try:
            label_widget = self.query_one("SelectCurrent #label", Static)
        except Exception:
            return

        raw = self._label_for(self.value)
        if raw is None:
            return

        # Budget: subtract outer borders (2), inner padding (4), arrow + gap (3)
        available = max(4, self.size.width - 9)
        label_widget.update(_truncate(raw, available))

    # ------------------------------------------------------------------
    # Lifecycle / reactive hooks
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        self.call_after_refresh(self._apply_truncation)

    def on_resize(self) -> None:
        self._apply_truncation()

    def watch_value(self, value: object) -> None:  # called after Select's own watcher
        self.call_after_refresh(self._apply_truncation)


# ── demo data ─────────────────────────────────────────────────────────────────


_DIFFICULTIES: list[tuple[str, str]] = [
    ("All difficulties", "all"),
    ("Easy", "easy"),
    ("Medium", "medium"),
    ("Hard", "hard"),
]

# Deliberately include long names to stress-test truncation.
_TOPICS: list[tuple[str, str]] = [
    ("All topics", "all"),
    ("Array", "array"),
    ("Dynamic Programming", "dp"),
    ("Sliding Window", "sliding_window"),
    ("Depth-First Search", "dfs"),
    ("Breadth-First Search (BFS)", "bfs"),
    ("Two Pointers", "two_pointers"),
    ("Binary Search", "binary_search"),
    ("Graph Theory & Shortest Paths", "graph"),
    ("Tree / Segment Tree", "segment_tree"),
    ("Monotonic Stack / Queue", "mono_stack"),
]


# ── demo app ──────────────────────────────────────────────────────────────────


class FilterTestApp(App):
    CSS = """
    Screen {
        background: #1a1a2e;
        color: #e0e0e0;
    }

    #filter-row {
        height: auto;
        padding: 1 2;
        border-bottom: solid #FF8205;
        align: left middle;
    }

    #difficulty-filter { width: 22; margin: 0 1; }
    #topic-filter      { width: 26; margin: 0 1; }

    Select {
        background: transparent;
        border: tall #888888;
        color: #e0e0e0;
    }
    Select:focus { border: tall #FF8205; }
    Select > SelectCurrent { background: transparent; color: #e0e0e0; }
    Select > SelectOverlay {
        background: #1a1a2e;
        border: tall #FF8205;
    }
    Select > SelectOverlay > .option-list--option { color: #e0e0e0; }
    Select > SelectOverlay > .option-list--option-highlighted {
        background: #FF8205;
        color: #000000;
    }

    #hint {
        height: auto;
        padding: 2 2;
        color: #888888;
        text-style: italic;
    }
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(
            TruncatedSelect(
                _DIFFICULTIES,
                value="all",
                id="difficulty-filter",
                allow_blank=False,
            ),
            TruncatedSelect(
                _TOPICS,
                value="all",
                id="topic-filter",
                allow_blank=False,
            ),
            id="filter-row",
        )
        yield Static(
            "Select a long topic above — the label should truncate with … "
            "rather than overflowing the filter box.\n\n"
            "Resize the terminal to watch live re-truncation.",
            id="hint",
        )


if __name__ == "__main__":
    FilterTestApp().run()
