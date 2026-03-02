"""ChallengeListScreen — browse, filter and search all challenges."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.events import Click
from textual.widgets import DataTable, Input, Select, Static
from textual import work
from textual.worker import Worker, WorkerState

from ...challenge_loader import Challenge, load_all_challenges
from ..widgets.challenge_table import ChallengeTable
from ..widgets.status_bar import StatusBar
from ..widgets.truncated_select import TruncatedSelect
from .base import BaseScreen
from .challenge_detail import ChallengeDetailScreen

_SOLUTION_TOGGLE_LABEL = "Has Solution"

_SOLVED_OPTIONS = [
    ("All Problems", "all"),
    ("Solved",       "yes"),
    ("Unsolved",     "no"),
]


class ChallengeListScreen(BaseScreen):
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
            ("Enter",  "Open challenge", None),
            ("Ctrl+R", "Reload challenges", None),
            ("Esc",    "go home",        self.action_pop_screen),
            ("Ctrl+Q", "Exit LeetVibe", self.action_quit_app),
        ]

        yield Horizontal(
            TruncatedSelect(
                [("All Difficulties", "all"), ("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")],
                value="all",
                id="difficulty-filter",
                allow_blank=False,
            ),
            TruncatedSelect(
                [("All Topics", "all")],
                value="all",
                id="topic-filter",
                allow_blank=False,
            ),
            TruncatedSelect(
                _SOLVED_OPTIONS,
                value="all",
                id="solved-filter",
                allow_blank=False,
            ),
            Static(_SOLUTION_TOGGLE_LABEL, id="btn-solution-toggle"),
            Input(placeholder="Search Problem…", id="search-input"),
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
        from ...cloud.auth import is_logged_in
        if not is_logged_in():
            self.query_one("#solved-filter", TruncatedSelect).add_class("hidden")

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
            table = self.query_one("#challenge-table", ChallengeTable)
            table.focus()
            if table.row_count > 0:
                table.move_cursor(row=0)
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
        try:
            sel = self.query_one("#difficulty-filter", TruncatedSelect)
            sel.set_class(value != "all", "filter-active")
        except Exception:
            pass

    def watch_filter_topic(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()
        try:
            sel = self.query_one("#topic-filter", TruncatedSelect)
            sel.set_class(value != "all", "filter-active")
        except Exception:
            pass

    def watch_filter_solution(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()
        try:
            self.query_one("#btn-solution-toggle", Static).set_class(value == "yes", "sol-active")
        except Exception:
            pass

    def watch_filter_solved(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()
        try:
            sel = self.query_one("#solved-filter", TruncatedSelect)
            sel.set_class(value != "all", "filter-active")
        except Exception:
            pass

    def watch_search_query(self, value: str) -> None:
        if self._all_challenges:
            self._repopulate()
        try:
            inp = self.query_one("#search-input", Input)
            inp.set_class(bool(value), "filter-active")
        except Exception:
            pass

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

    def on_click(self, event: Click) -> None:
        if getattr(event.widget, "id", None) == "btn-solution-toggle":
            self.filter_solution = "yes" if self.filter_solution == "all" else "all"

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "difficulty-filter":
            self.filter_difficulty = str(event.value)
        elif event.select.id == "topic-filter":
            self.filter_topic = str(event.value)
        elif event.select.id == "solved-filter":
            self.filter_solved = str(event.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self.search_query = event.value

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        challenge_id = str(event.row_key.value)
        challenge = next(
            (c for c in self._all_challenges if c.id == challenge_id), None
        )
        if challenge:
            if self._mode == "interview":
                from .agent_session import AgentSessionScreen
                self.app.push_screen(AgentSessionScreen(challenge, mode="interview"))
            else:
                index = self._all_challenges.index(challenge)
                self.app.push_screen(
                    ChallengeDetailScreen(challenge, self._all_challenges, index, self._mode)
                )

    def action_reload(self) -> None:
        self._all_challenges = []
        self.query_one("#challenge-table", ChallengeTable).clear()
        self._load_challenges()
