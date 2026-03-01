"""ChallengeListScreen — browse, filter and search all challenges."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Select
from textual import work
from textual.worker import Worker, WorkerState

from ...challenge_loader import Challenge, load_all_challenges
from ..widgets.challenge_table import ChallengeTable
from ..widgets.status_bar import StatusBar
from ..widgets.truncated_select import TruncatedSelect
from .challenge_detail import ChallengeDetailScreen

_TOGGLE_INACTIVE_LABEL = "Solution: All"
_TOGGLE_ACTIVE_LABEL   = "✓  Has Solution"

# 3-state cycle for solved filter
_SOLVED_LABELS = {
    "all": "Solved: All",
    "yes": "✓  Solved Only",
    "no":  "✗  Unsolved",
}
_SOLVED_NEXT = {"all": "yes", "yes": "no", "no": "all"}


class ChallengeListScreen(Screen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("ctrl+q", "quit_app", "Quit"),
        Binding("ctrl+r", "reload", "Reload", show=False),
    ]

    filter_difficulty: reactive[str] = reactive("all")
    filter_topic: reactive[str] = reactive("all")
    filter_solution: reactive[str] = reactive("all")
    filter_solved: reactive[str] = reactive("all")
    search_query: reactive[str] = reactive("")

    def __init__(self, mode: str = "learn") -> None:
        super().__init__()
        self._mode = mode
        self._all_challenges: list[Challenge] = []
        self._filtered_count: int = 0
        self._solved_slugs: set[str] | None = None

    def compose(self) -> ComposeResult:
        footer_hints = [
            ("Ctrl+Q", "Exit LeetVibe", self.action_quit_app),
            ("Esc",    "Home",          self.action_pop_screen),
            ("Enter",  "Open challenge", None),
        ]

        yield Horizontal(
            TruncatedSelect(
                [("All difficulties", "all"), ("Easy", "easy"), ("Medium", "medium"),
                 ("Hard", "hard"), ("Trading", "trading")],
                value="all",
                id="difficulty-filter",
                allow_blank=False,
            ),
            TruncatedSelect(
                [("All topics", "all")],
                value="all",
                id="topic-filter",
                allow_blank=False,
            ),
            Button(_TOGGLE_INACTIVE_LABEL, id="btn-solution-toggle"),
            Button(_SOLVED_LABELS["all"], id="btn-solved-toggle"),
            Input(placeholder="Search title…", id="search-input"),
            id="list-header",
        )
        yield ChallengeTable(id="challenge-table")
        yield StatusBar(
            hints=footer_hints,
            show_count=True,
            hints_centered=True,
            id="list-status",
        )

    def on_mount(self) -> None:
        self._load_challenges()
        self._load_solved_slugs()

    @work(thread=True)
    def _load_challenges(self) -> list[Challenge]:
        return load_all_challenges()

    @work(thread=True)
    def _load_solved_slugs(self) -> set[str]:
        from ...cloud.db import get_solved_slugs
        return get_solved_slugs()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "_load_challenges" and event.state == WorkerState.SUCCESS:
            self._all_challenges = event.worker.result or []
            self._populate_topic_filter()
            self._repopulate()
        elif event.worker.name == "_load_solved_slugs" and event.state == WorkerState.SUCCESS:
            self._solved_slugs = event.worker.result or set()
            if self._all_challenges:
                self._repopulate()

    def _populate_topic_filter(self) -> None:
        topics = sorted({t for ch in self._all_challenges for t in ch.topics if t})
        options = [("All topics", "all")] + [(t, t) for t in topics]
        self.query_one("#topic-filter", TruncatedSelect).set_options(options)

    def watch_filter_difficulty(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()

    def watch_filter_topic(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()

    def watch_filter_solution(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()
        try:
            btn = self.query_one("#btn-solution-toggle", Button)
            if value == "yes":
                btn.label = _TOGGLE_ACTIVE_LABEL
                btn.add_class("sol-active")
            else:
                btn.label = _TOGGLE_INACTIVE_LABEL
                btn.remove_class("sol-active")
        except Exception:
            pass

    def watch_filter_solved(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()
        try:
            btn = self.query_one("#btn-solved-toggle", Button)
            btn.label = _SOLVED_LABELS[value]
            if value == "yes":
                btn.add_class("sol-active")
                btn.remove_class("solved-no")
            elif value == "no":
                btn.remove_class("sol-active")
                btn.add_class("solved-no")
            else:
                btn.remove_class("sol-active", "solved-no")
        except Exception:
            pass

    def watch_search_query(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()

    def _repopulate(self) -> None:
        table = self.query_one("#challenge-table", ChallengeTable)
        filtered = table.filter(
            self._all_challenges,
            self.filter_difficulty,
            self.filter_topic,
            self.search_query,
            self.filter_solution,
            self._solved_slugs,
            self.filter_solved,
        )
        self._filtered_count = len(filtered)
        self.query_one("#list-status", StatusBar).update_count(
            self._filtered_count, len(self._all_challenges)
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-solution-toggle":
            # 2-state toggle: all ↔ has-solution
            self.filter_solution = "yes" if self.filter_solution == "all" else "all"
        elif event.button.id == "btn-solved-toggle":
            # 3-state cycle: all → yes → no → all
            self.filter_solved = _SOLVED_NEXT[self.filter_solved]

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "difficulty-filter":
            self.filter_difficulty = str(event.value)
        elif event.select.id == "topic-filter":
            self.filter_topic = str(event.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self.search_query = event.value

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        challenge_id = str(event.row_key.value)
        challenge = next(
            (c for c in self._all_challenges if c.id == challenge_id), None
        )
        if challenge:
            index = self._all_challenges.index(challenge)
            self.app.push_screen(
                ChallengeDetailScreen(challenge, self._all_challenges, index, self._mode)
            )

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_reload(self) -> None:
        self._all_challenges = []
        self.query_one("#challenge-table", ChallengeTable).clear()
        self._load_challenges()
