"""Problem detail card widget — left panel content."""

from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Resize
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ...problem_loader import Problem

_DIFF_ICONS = {"easy": "●", "medium": "◆", "hard": "★"}
_DIFF_STYLES = {
    "easy": "#00C44F",
    "medium": "#FFB300",
    "hard": "#E53935",
}

# padding (1 left + 1 right) + margin-right (1) from the `.badge` TCSS rule
_BADGE_CHROME_WIDTH = 3


class TagsRow(Horizontal):
    """A single row of badges; whatever doesn't fit collapses into a "+N" badge."""

    def __init__(self, badges: list[tuple[str, str]], **kwargs) -> None:
        super().__init__(**kwargs)
        self._badges = badges
        self._last_width = -1

    async def on_resize(self, event: Resize) -> None:
        width = event.size.width
        if width <= 0 or width == self._last_width:
            return
        self._last_width = width

        shown, hidden = self._fit_badges(width)
        children = [
            Static(label, classes=f"badge {extra_class}".strip())
            for label, extra_class in shown
        ]
        if hidden:
            children.append(Static(f"+{hidden}", classes="badge badge-more"))

        await self.remove_children()
        await self.mount_all(children)

    def _fit_badges(self, width: int) -> tuple[list[tuple[str, str]], int]:
        widths = [cell_len(label) + _BADGE_CHROME_WIDTH for label, _ in self._badges]
        total = len(self._badges)
        if sum(widths) <= width:
            return list(self._badges), 0

        shown = 0
        running = 0
        for i, badge_width in enumerate(widths):
            hidden_after = total - (i + 1)
            indicator_width = (
                cell_len(f"+{hidden_after}") + _BADGE_CHROME_WIDTH if hidden_after else 0
            )
            if running + badge_width + indicator_width > width:
                break
            running += badge_width
            shown = i + 1

        return list(self._badges[:shown]), total - shown


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
        badges: list[tuple[str, str]] = [
            (f"{diff_icon} {ch.difficulty.capitalize()}", f"badge-{ch.difficulty}")
        ]
        badges += [(topic, "badge-topic") for topic in ch.topics[:5]]
        if ch.hints:
            badges.append((f"💡 {len(ch.hints)} Hints", ""))
        yield TagsRow(badges, id="tags-row")

        # Description — raw LeetCode content, never Rich-markup-templated, and
        # example blocks routinely contain literal "[...]" (e.g. Input: equations
        # = ["a!=b","b!=a"]) that a markup-enabled Static tries to parse as tags
        # and crashes on. markup=False renders it as plain, literal text instead.
        yield Static(
            ch.description or "No description available.",
            id="card-description",
            markup=False,
        )

        # Hints (toggled with Ctrl+G) — only rendered when hints exist. Same raw-
        # content risk as the description above.
        if ch.hints:
            yield Static("💡 Hints hidden — press Ctrl+G to reveal", id="hints-placeholder")
            yield Static("", id="hints-content", classes="hidden", markup=False)

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
