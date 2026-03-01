"""Challenge DataTable widget with filtering support."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import DataTable

from ...challenge_loader import Challenge

_DIFF_ICONS = {"easy": "●", "medium": "◆", "hard": "★", "trading": "₿"}
_DIFF_STYLES = {
    "easy": "bold #00C44F",
    "medium": "bold #FFB300",
    "hard": "bold #E53935",
    "trading": "bold #00BCD4",
}


def _difficulty_badge(difficulty: str) -> Text:
    icon = _DIFF_ICONS.get(difficulty, "·")
    style = _DIFF_STYLES.get(difficulty, "white")
    return Text(f"{icon} {difficulty.upper()}", style=style)


class ChallengeTable(DataTable):
    """DataTable pre-configured for challenge display."""

    DEFAULT_CSS = """
    ChallengeTable {
        height: 1fr;
    }
    """

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Title", "Difficulty", "Topics", "Solution")

    def populate(self, challenges: list[Challenge]) -> None:
        """Clear and repopulate the table with the given challenges."""
        self.clear()
        for ch in challenges:
            solution = (
                Text("✓ yes", style="bold #00C44F")
                if ch.has_solutions
                else Text("✗ no", style="dim #888888")
            )
            self.add_row(
                ch.title,
                _difficulty_badge(ch.difficulty),
                Text(", ".join(ch.topics[:3]) or "—", style="dim"),
                solution,
                key=ch.id,
            )

    def filter(
        self,
        challenges: list[Challenge],
        difficulty: str,
        topic: str,
        query: str,
        has_solution: str = "all",
    ) -> list[Challenge]:
        """Return filtered subset and repopulate table."""
        filtered = challenges

        if difficulty and difficulty != "all":
            filtered = [c for c in filtered if c.difficulty == difficulty]

        if topic and topic != "all":
            filtered = [c for c in filtered if topic in c.topics]

        if has_solution == "yes":
            filtered = [c for c in filtered if c.has_solutions]
        elif has_solution == "no":
            filtered = [c for c in filtered if not c.has_solutions]

        if query:
            q = query.lower()
            filtered = [c for c in filtered if q in c.title.lower()]

        self.populate(filtered)
        return filtered
