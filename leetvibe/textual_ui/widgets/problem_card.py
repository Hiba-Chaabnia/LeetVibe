"""Problem detail card widget — left panel content."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ...problem_loader import Problem

_DIFF_ICONS = {"easy": "●", "medium": "◆", "hard": "★", "trading": "₿"}
_DIFF_STYLES = {
    "easy": "#00C44F",
    "medium": "#FFB300",
    "hard": "#E53935",
    "trading": "#00BCD4",
}


class ProblemCard(Widget):
    """Displays problem title, tags, description, and toggleable hints."""

    show_hints: reactive[bool] = reactive(False)

    def __init__(self, problem: Problem, **kwargs) -> None:
        super().__init__(**kwargs)
        self._problem = problem

    def compose(self) -> ComposeResult:
        ch = self._problem
        diff_icon = _DIFF_ICONS.get(ch.difficulty, "·")

        # Title
        title_text = Text()
        title_text.append(ch.title, style="bold white")
        yield Static(title_text, id="card-title")

        # Tags row: difficulty badge + topic badges + hints count
        with Horizontal(id="tags-row"):
            yield Static(
                f"{diff_icon} {ch.difficulty.capitalize()}",
                classes=f"badge badge-{ch.difficulty}",
            )
            for topic in ch.topics[:5]:
                yield Static(topic, classes="badge badge-topic")
            if ch.hints:
                yield Static(f"💡 {len(ch.hints)} Hints", classes="badge")

        # Description
        yield Static(
            ch.description or "No description available.",
            id="card-description",
        )

        # Hints (toggled with H key) — only rendered when hints exist
        if ch.hints:
            yield Static("💡 Hints hidden — press H to reveal", id="hints-placeholder")
            yield Static("", id="hints-content", classes="hidden")

    def watch_show_hints(self, show: bool) -> None:
        ch = self._problem
        if not ch.hints:
            return

        placeholder = self.query_one("#hints-placeholder")
        hints_content = self.query_one("#hints-content", Static)

        if show:
            lines = "\n".join(
                f"💡 Hint {i + 1}: {h}" for i, h in enumerate(ch.hints)
            )
            hints_content.update(lines)
            placeholder.add_class("hidden")
            hints_content.remove_class("hidden")
        else:
            placeholder.remove_class("hidden")
            hints_content.add_class("hidden")
