"""Challenge detail card widget — left panel content."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ...challenge_loader import Challenge

_DIFF_ICONS = {"easy": "●", "medium": "◆", "hard": "★", "trading": "₿"}
_DIFF_STYLES = {
    "easy": "#00C44F",
    "medium": "#FFB300",
    "hard": "#E53935",
    "trading": "#00BCD4",
}


class ChallengeCard(Widget):
    """Displays challenge title, tags, description, and toggleable hints."""

    show_hints: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    ChallengeCard {
        height: auto;
        text-align: left;
    }
    ChallengeCard #card-title {
        height: auto;
        padding: 0 0 1 0;
        color: white;
        text-style: bold;
        text-align: left;
    }
    ChallengeCard #tags-row {
        height: auto;
        padding: 0 0 0 0;
    }
    ChallengeCard .badge {
        height: 1;
        width: auto;
        padding: 0 1;
        margin: 0 1 0 0;
        background: #2a2a2a;
        color: #aaaaaa;
    }
    ChallengeCard .badge-easy   { background: #1a3a1a; color: #00C44F; }
    ChallengeCard .badge-medium { background: #3a2a00; color: #FFB300; }
    ChallengeCard .badge-hard   { background: #3a1010; color: #E53935; }
    ChallengeCard .badge-trading { background: #0a2a2a; color: #00BCD4; }
    ChallengeCard .badge-topic  { background: #252525; color: #aaaaaa; }
    ChallengeCard #card-description {
        height: auto;
        color: #e0e0e0;
        padding: 1 0;
        border-top: solid #333333;
        margin-top: 1;
        text-align: left;
    }
    ChallengeCard #hints-placeholder {
        color: #888888;
        text-style: italic;
        padding: 1 0;
        border-top: dashed #444444;
        margin-top: 1;
    }
    ChallengeCard #hints-content {
        height: auto;
        color: #FFB300;
        padding: 1 0;
        border-top: dashed #888888;
        margin-top: 1;
    }
    ChallengeCard .hidden {
        display: none;
    }
    """

    def __init__(self, challenge: Challenge, **kwargs) -> None:
        super().__init__(**kwargs)
        self._challenge = challenge

    def compose(self) -> ComposeResult:
        ch = self._challenge
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

        # Hints (toggled with H key)
        yield Static("💡 Hints hidden — press H to reveal", id="hints-placeholder")
        yield Static("", id="hints-content", classes="hidden")

    def watch_show_hints(self, show: bool) -> None:
        ch = self._challenge
        placeholder = self.query_one("#hints-placeholder")
        hints_content = self.query_one("#hints-content", Static)

        if show and ch.hints:
            lines = "\n".join(
                f"💡 Hint {i + 1}: {h}" for i, h in enumerate(ch.hints)
            )
            hints_content.update(lines)
            placeholder.add_class("hidden")
            hints_content.remove_class("hidden")
        else:
            placeholder.remove_class("hidden")
            hints_content.add_class("hidden")
