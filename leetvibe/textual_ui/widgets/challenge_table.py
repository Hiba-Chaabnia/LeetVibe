"""Challenge DataTable widget with filtering support."""

from __future__ import annotations

from rich.text import Text  # used for gradient column headers
from textual.widgets import DataTable

from ...challenge_loader import Challenge

_DIFF_STYLES: dict[str, tuple[str, str]] = {
    "easy":   ("Easy",   "#FFD700"),  # GOLD
    "medium": ("Medium", "#FF8205"),  # FIRE
    "hard":   ("Hard",   "#E92700"),  # LAVA
}

# Problem and Topics share the remaining width equally after fixed columns.
# Fixed columns (Difficulty, Solved, Solution) are each 10%.
# With Solved:    remaining = 70%  → Problem=35%, Topics=35%
# Without Solved: remaining = 80%  → Problem=40%, Topics=40%
_COLS_WITH_SOLVED: list[tuple[str, float]] = [
    ("Problem",    0.40),
    ("Difficulty", 0.10),
    ("Topics",     0.40),
    ("Solved",     0.05),
    ("Solution",   0.05),
]

_COLS_NO_SOLVED: list[tuple[str, float]] = [
    ("Problem",    0.425),
    ("Difficulty", 0.10),
    ("Topics",     0.425),
    ("Solution",   0.05),
]

# Gradient color per column header (GOLD → LAVA left to right)
_HEADER_COLORS: dict[str, str] = {
    "Problem":    "#FFD700",  # GOLD
    "Difficulty": "#FFAF00",  # HONEY
    "Topics":     "#FF8205",  # FIRE
    "Solved":     "#FA500F",  # EMBER
    "Solution":   "#E92700",  # LAVA
}


def _truncate(text: str, max_width: int) -> str:
    if len(text) > max_width:
        return text[: max_width - 1] + "…"
    return text


class ChallengeTable(DataTable):
    """DataTable pre-configured for challenge display."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self._col_widths: dict[str, int] = {}
        from ...cloud.auth import is_logged_in
        self._show_solved: bool = is_logged_in()
        self._setup_columns()

    def _setup_columns(self) -> None:
        available = max(60, self.app.size.width - 4)
        ratios = _COLS_WITH_SOLVED if self._show_solved else _COLS_NO_SOLVED
        for name, ratio in ratios:
            w = max(6, int(available * ratio))
            self._col_widths[name] = w
            label = Text(name, style=f"bold {_HEADER_COLORS[name]}", justify="center")
            self.add_column(label, width=w)

    def populate(
        self,
        challenges: list[Challenge],
        solved_slugs: set[str] | None = None,
    ) -> None:
        """Clear and repopulate the table with the given challenges."""
        self.clear()
        prob_w   = self._col_widths.get("Problem", 40)
        topics_w = self._col_widths.get("Topics",  30)
        for ch in challenges:
            topics_str = ", ".join(ch.topics[:3]) or "—"
            label, color = _DIFF_STYLES.get(ch.difficulty, (ch.difficulty.capitalize(), "#888888"))
            row: list = [
                _truncate(ch.title, prob_w),
                Text(label, style=f"bold {color}", justify="center"),
                _truncate(topics_str, topics_w),
            ]
            if self._show_solved:
                is_solved = solved_slugs is not None and ch.id in solved_slugs
                row.append(Text("✓" if is_solved else "—", justify="center"))
            row.append(Text("✓" if ch.has_solutions else "✗", justify="center"))
            self.add_row(*row, key=ch.id)

    def filter(
        self,
        challenges: list[Challenge],
        difficulty: str,
        topic: str,
        query: str,
        has_solution: str = "all",
        solved_slugs: set[str] | None = None,
        is_solved: str = "all",
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

        if solved_slugs is not None and self._show_solved:
            if is_solved == "yes":
                filtered = [c for c in filtered if c.id in solved_slugs]
            elif is_solved == "no":
                filtered = [c for c in filtered if c.id not in solved_slugs]

        if query:
            q = query.lower()
            filtered = [c for c in filtered if q in c.title.lower()]

        self.populate(filtered, solved_slugs)
        return filtered
