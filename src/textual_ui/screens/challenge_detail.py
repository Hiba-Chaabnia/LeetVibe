"""ChallengeDetailScreen — LeetCode-style two-panel layout with custom top bar."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from rich.text import Text as RichText

from textual.widgets import (
    Button,
    DataTable,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)


class CodeEditor(TextArea):
    """TextArea with Ctrl+A remapped to select-all (instead of line-start)."""

    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False, priority=True),
    ]
from textual.worker import Worker, WorkerState

from ...challenge_loader import Challenge
from ...code_runner import CaseResult, run_tests
from ..widgets.challenge_card import ChallengeCard
from ..widgets.status_bar import StatusBar

# ── Auth helper (fast local file check — safe to call in compose) ──────────────
def _is_logged_in() -> bool:
    try:
        from ...cloud.auth import load_session
        return bool(load_session())
    except Exception:
        return False

# ── Defaults ───────────────────────────────────────────────────────────────────
_DEFAULT_PYTHON = "class Solution:\n    def solve(self):\n        pass\n"

# ── UI icons (standard Unicode — no Nerd Font required) ───────────────────────
_I_LIST   = "≡"    # Problem List
_I_PREV   = "←"    # Prev
_I_NEXT   = "→"    # Next
_I_RUN    = "▶"    # Run
_I_SUBMIT = "↑"    # Submit
_I_EYE    = "◉"    # Solution
_I_CASE   = "▤"    # Testcase tab
_I_CHART  = "▦"    # Test Result tab
_I_BULB   = "✦"    # Solution tab / Hints
_I_BOLT   = "⚡"   # Session (footer)



class _TopBar(Horizontal):
    """Top navigation bar — excluded from maximize."""
    ALLOW_MAXIMIZE = False


class ChallengeDetailScreen(Screen):
    """Full problem view: custom top bar, description panel, code editor, tabs."""

    BINDINGS = [
        Binding("escape",  "pop_screen",     "Problem List"),
        Binding("ctrl+q",  "quit_app",       "Exit LeetVibe"),
        Binding("ctrl+p",  "open_palette",   "Palette",       show=False),
        Binding("left",    "prev_challenge", "Prev",          show=False),
        Binding("right",   "next_challenge", "Next",          show=False),
        Binding("h",       "toggle_hints",   "Hints"),
        Binding("s",       "start_session",  "Solve with Vibe"),
    ]

    DEFAULT_CSS = """
    /* ── Top bar ─────────────────────────────────────────────────── */
    _TopBar {
        height: 3;
        background: #1a1a1a;
        border-bottom: solid #FF8205;
        padding: 0 1;
    }
    #nav-section {
        width: 2fr;
        align: left middle;
    }
    #action-section {
        width: 1fr;
        align: center middle;
    }
    #sol-section {
        width: 1fr;
        align: right middle;
    }
    /* All top-bar buttons share base compact style */
    #btn-problem-list, #btn-prev, #btn-next,
    #btn-run, #btn-submit, #btn-feedback, #btn-solution {
        border: none;
        background: transparent;
        padding: 0 1;
        min-width: 0;
        height: 1;
    }
    #btn-problem-list, #btn-prev, #btn-next { color: #aaaaaa; }
    #btn-prev:disabled, #btn-next:disabled   { color: #444444; }
    #btn-run                                 { color: #00C44F; }
    #btn-submit                              { color: #4A9EFF; }
    #btn-feedback                            { color: #888888; }
    #btn-solution                            { color: #FF8205; }
    #btn-problem-list:hover, #btn-prev:hover, #btn-next:hover {
        background: #2a2a2a;
        color: #e0e0e0;
    }
    #btn-run:hover      { background: #1a3a1a; }
    #btn-submit:hover   { background: #102040; }
    #btn-submit:disabled { color: #444444; }
    #btn-feedback:hover { background: #2a2a2a; color: #e0e0e0; }
    #btn-solution:hover { background: #3a2200; color: #FFB300; }

    /* ── Main body ───────────────────────────────────────────────── */
    #detail-body {
        height: 1fr;
        padding: 0 1;
        margin-bottom: 2;
    }

    /* ── Left panel ──────────────────────────────────────────────── */
    #left-panel {
        width: 1fr;
        border: round #FF8205;
        margin: 0 1 0 0;
    }
    #left-scroll {
        height: 1fr;
        padding: 1 2;
    }

    /* ── Right panel ─────────────────────────────────────────────── */
    #right-panel {
        width: 1fr;
        border: round #FF8205;
        margin: 0 0 0 1;
    }

    #editor-panel {
        height: 4fr;
        border-bottom: solid #FF8205;
    }
    #code-editor { height: 1fr; }

    /* ── Bottom tabs ─────────────────────────────────────────────── */
    #testcase-tabs { height: 1fr; }
    #testcase-table, #result-table { height: 1fr; }
    #solution-explanation {
        height: auto;
        color: #e0e0e0;
        padding: 1 2;
        text-align: left;
    }
    #no-solution-msg {
        padding: 1 2;
        color: #888888;
        text-style: italic;
    }
    """

    def __init__(
        self,
        challenge: Challenge,
        challenges: list[Challenge],
        index: int,
        mode: str = "learn",
    ) -> None:
        super().__init__()
        self._challenge = challenge
        self._challenges = challenges
        self._index = index
        self._mode = mode
        self._solution_shown = False
        self._logged_in = _is_logged_in()
        self._cloud_session_id: str | None = None

    def compose(self) -> ComposeResult:
        ch = self._challenge
        at_start = self._index == 0
        at_end   = self._index == len(self._challenges) - 1

        # ── Custom top bar ──────────────────────────────────────────────
        with _TopBar(id="top-bar"):
            with Horizontal(id="nav-section"):
                yield Button(f"{_I_LIST}  Problem List", id="btn-problem-list")
                yield Button(f"{_I_PREV}  Prev",         id="btn-prev",     disabled=at_start)
                yield Button(f"{_I_NEXT}  Next",         id="btn-next",     disabled=at_end)
            with Horizontal(id="action-section"):
                yield Button(f"{_I_RUN}  Run",           id="btn-run")
                if self._logged_in:
                    yield Button(f"{_I_SUBMIT}  Submit", id="btn-submit")
                    yield Button("✉  Feedback",          id="btn-feedback")
            with Horizontal(id="sol-section"):
                if ch.has_solutions:
                    yield Button(f"{_I_EYE}  Solution",  id="btn-solution")

        # ── Main body ───────────────────────────────────────────────────
        with Horizontal(id="detail-body"):

            # Left: scrollable description
            with Vertical(id="left-panel"):
                with VerticalScroll(id="left-scroll"):
                    yield ChallengeCard(ch, id="challenge-card")

            # Right: editor (top) + tabs (bottom)
            with Vertical(id="right-panel"):

                with Vertical(id="editor-panel"):
                    yield CodeEditor(
                        ch.python_snippet or _DEFAULT_PYTHON,
                        language="python",
                        theme="monokai",
                        soft_wrap=False,
                        tab_behavior="indent",
                        show_line_numbers=True,
                        id="code-editor",
                    )

                with TabbedContent(id="testcase-tabs"):
                    with TabPane(f"{_I_CASE}  Testcase", id="tab-testcase"):
                        yield DataTable(
                            id="testcase-table",
                            show_cursor=False,
                            zebra_stripes=True,
                        )
                    with TabPane(f"{_I_CHART}  Test Result", id="tab-result"):
                        yield DataTable(
                            id="result-table",
                            show_cursor=False,
                            zebra_stripes=True,
                        )
                    with TabPane(f"{_I_BULB}  Solution Explanation",
                                 id="tab-solution-explanation"):
                        with VerticalScroll():
                            if ch.has_solutions:
                                yield Static(
                                    ch.solution_explanation or "",
                                    id="solution-explanation",
                                )
                            else:
                                yield Static(
                                    "No solution available for this challenge.",
                                    id="no-solution-msg",
                                )

        yield StatusBar(
            hints=[
                ("H",      "Hints",           self.action_toggle_hints),
                ("S",      "Solve with Vibe", self.action_start_session),
                ("Ctrl+P", "Palette",         self.action_open_palette),
                ("Esc",    "Problem List",    self.action_pop_screen),
                ("Ctrl+Q", "Exit LeetVibe",   self.action_quit_app),
            ],
            show_count=False,
            id="detail-status",
        )

    # ── Lifecycle ──────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self.query_one("#testcase-tabs", TabbedContent).hide_tab(
            "tab-solution-explanation"
        )
        self._populate_testcase_table()
        self._setup_result_table()

    # ── Helpers ────────────────────────────────────────────────────────

    def _populate_testcase_table(self) -> None:
        ch = self._challenge
        table = self.query_one("#testcase-table", DataTable)
        table.add_columns("#", "Input", "Expected Output")
        for i, inputs in enumerate(ch.test_cases[:5], 1):
            expected = ch.expected_outputs[i - 1] if i - 1 < len(ch.expected_outputs) else "—"
            input_str = "\n".join(str(v) for v in inputs)
            table.add_row(str(i), input_str, expected)

    def _setup_result_table(self) -> None:
        table = self.query_one("#result-table", DataTable)
        table.add_columns("#", "Input", "Expected", "Actual Output", "Status")

    def _load_editor(self, code: str) -> None:
        self.query_one("#code-editor", TextArea).load_text(code)

    def _toggle_solution(self) -> None:
        ch = self._challenge
        tabs = self.query_one("#testcase-tabs", TabbedContent)
        if self._solution_shown:
            tabs.hide_tab("tab-solution-explanation")
            self._load_editor(ch.python_snippet or _DEFAULT_PYTHON)
            self._solution_shown = False
        else:
            if not ch.has_solutions:
                self.notify(
                    "No solution available for this challenge.",
                    severity="warning",
                )
                return
            self._load_editor(ch.python_solution or "# No Python solution available.")
            tabs.show_tab("tab-solution-explanation")
            tabs.active = "tab-solution-explanation"
            self._solution_shown = True

    # ── Event handlers ─────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id

        if btn == "btn-problem-list":
            self.app.pop_screen()

        elif btn == "btn-prev" and self._index > 0:
            self.app.switch_screen(
                ChallengeDetailScreen(
                    self._challenges[self._index - 1],
                    self._challenges,
                    self._index - 1,
                    self._mode,
                )
            )

        elif btn == "btn-next" and self._index < len(self._challenges) - 1:
            self.app.switch_screen(
                ChallengeDetailScreen(
                    self._challenges[self._index + 1],
                    self._challenges,
                    self._index + 1,
                    self._mode,
                )
            )

        elif btn == "btn-run":
            code = self.query_one("#code-editor", TextArea).text
            ch = self._challenge
            snippet = ch.python_snippet or _DEFAULT_PYTHON
            self.query_one("#btn-run", Button).disabled = True
            self.query_one("#result-table", DataTable).clear()
            tabs = self.query_one("#testcase-tabs", TabbedContent)
            tabs.active = "tab-result"
            self._run_code(code, snippet, ch.test_cases, ch.expected_outputs)

        elif btn == "btn-submit":
            code = self.query_one("#code-editor", TextArea).text
            ch = self._challenge
            snippet = ch.python_snippet or _DEFAULT_PYTHON
            self.query_one("#btn-submit", Button).disabled = True
            self._submit_code(code, snippet, ch.test_cases, ch.expected_outputs)

        elif btn == "btn-feedback":
            from .feedback import FeedbackModal
            self.app.push_screen(
                FeedbackModal(
                    problem_slug=self._challenge.id,
                    session_id=self._cloud_session_id,
                ),
                self._on_feedback_result,
            )

        elif btn == "btn-solution":
            self._toggle_solution()

    # ── Run / Submit workers ────────────────────────────────────────────

    @work(thread=True)
    def _run_code(
        self,
        code: str,
        snippet: str,
        test_cases: list[list[str]],
        expected_outputs: list[str],
    ) -> list[CaseResult]:
        return run_tests(code, snippet, test_cases, expected_outputs)

    @work(thread=True)
    def _submit_code(
        self,
        code: str,
        snippet: str,
        test_cases: list[list[str]],
        expected_outputs: list[str],
    ) -> list[CaseResult]:
        return run_tests(code, snippet, test_cases, expected_outputs)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "_run_code":
            self.query_one("#btn-run", Button).disabled = False
            if event.state == WorkerState.SUCCESS:
                self._display_results(event.worker.result or [])
            elif event.state == WorkerState.ERROR:
                table = self.query_one("#result-table", DataTable)
                table.clear()
                table.add_row("—", "—", "—", "—", RichText("Internal error", style="bold red"))

        elif event.worker.name == "_submit_code":
            if self._logged_in:
                try:
                    self.query_one("#btn-submit", Button).disabled = False
                except Exception:
                    pass
            if event.state == WorkerState.SUCCESS:
                self._handle_submit_results(event.worker.result or [])
            elif event.state == WorkerState.ERROR:
                self.notify("Submission failed due to an error.", severity="error")

    def _handle_submit_results(self, results: list[CaseResult]) -> None:
        """Check submit results; mark solved in DB if all pass."""
        if not results:
            self.notify("No test cases to run.", severity="warning")
            return

        passed = sum(1 for r in results if r.passed is True)
        total = len(results)

        if passed == total:
            self._display_results(results)
            self.query_one("#testcase-tabs", TabbedContent).active = "tab-result"
            self.notify(
                f"All {total} test case(s) passed! Saving solution…",
                title="Accepted",
                severity="information",
            )
            code = self.query_one("#code-editor", TextArea).text
            self._save_solution(code)
        else:
            self._display_results(results)
            self.query_one("#testcase-tabs", TabbedContent).active = "tab-result"
            self.notify(
                f"{passed}/{total} test case(s) passed. Keep going!",
                title="Wrong Answer",
                severity="warning",
            )

    @work(thread=True)
    def _save_solution(self, code: str) -> None:
        from ...cloud.db import mark_solved
        ch = self._challenge
        ok = mark_solved(ch.id, ch.difficulty, code)
        self.app.call_from_thread(self._on_solution_saved, ok)

    def _on_solution_saved(self, ok: bool) -> None:
        if ok:
            self.notify("Solution saved to your profile!", title="Solved", severity="information")
        else:
            self.notify(
                "Solved locally, but couldn't save to cloud.",
                title="Sync error",
                severity="warning",
            )

    def _on_feedback_result(self, submitted: bool) -> None:
        if submitted:
            self.notify("Feedback sent. Thank you!", severity="information")

    @staticmethod
    def _fmt_value(v: object) -> str:
        """Format a Python value to match LeetCode conventions (lowercase booleans)."""
        if isinstance(v, bool):
            return "true" if v else "false"
        return repr(v)

    def _display_results(self, results: list[CaseResult]) -> None:
        table = self.query_one("#result-table", DataTable)
        table.clear()
        for r in results:
            input_str = ",  ".join(self._fmt_value(v) for v in r.inputs) if r.inputs else "—"
            expected = r.expected or "—"
            if r.error:
                actual = RichText(r.error, style="red")
                status = RichText("✗  Error", style="bold red")
            else:
                actual = RichText(self._fmt_value(r.output), style="white")
                if r.passed is True:
                    status = RichText("✓  Pass", style="bold #00C44F")
                elif r.passed is False:
                    status = RichText("✗  Fail", style="bold yellow")
                else:
                    status = RichText("—", style="dim")
            table.add_row(str(r.case_num), input_str, expected, actual, status)

    # ── Actions ────────────────────────────────────────────────────────

    def action_toggle_hints(self) -> None:
        self.query_one("#challenge-card", ChallengeCard).show_hints ^= True

    def action_start_session(self) -> None:
        from .agent_session import AgentSessionScreen

        user_code = self.query_one("#code-editor", TextArea).text
        self.app.push_screen(
            AgentSessionScreen(self._challenge, mode=self._mode, user_code=user_code)
        )

    def action_prev_challenge(self) -> None:
        if self._index > 0:
            self.app.switch_screen(
                ChallengeDetailScreen(
                    self._challenges[self._index - 1],
                    self._challenges,
                    self._index - 1,
                    self._mode,
                )
            )

    def action_next_challenge(self) -> None:
        if self._index < len(self._challenges) - 1:
            self.app.switch_screen(
                ChallengeDetailScreen(
                    self._challenges[self._index + 1],
                    self._challenges,
                    self._index + 1,
                    self._mode,
                )
            )

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_open_palette(self) -> None:
        self.call_later(self.app.action_command_palette)
