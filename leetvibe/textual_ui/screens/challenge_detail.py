"""ChallengeDetailScreen — LeetCode-style two-panel layout with custom top bar."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
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
from ...cloud.auth import is_logged_in
from ...code_runner import CaseResult, run_tests
from ..widgets.challenge_card import ChallengeCard
from ..widgets.status_bar import StatusBar
from .base import BaseScreen

# ── Defaults ───────────────────────────────────────────────────────────────────
_DEFAULT_PYTHON = "class Solution:\n    def solve(self):\n        pass\n"

# ── UI icons (standard Unicode — no Nerd Font required) ───────────────────────
_I_PREV   = "←"    # Prev
_I_NEXT   = "→"    # Next
_I_RUN    = "▶"    # Run
_I_SUBMIT = "↑"    # Submit
_I_CASE   = "▤"    # Test Cases tab
_I_CHART  = "▦"    # Test Results tab
_I_BULB   = "✦"    # Solution tab / Hints
_I_BOLT   = "⚡"   # Session (footer)



class _DetailTopBar(Horizontal):
    """Top navigation bar with nav, action and solution buttons."""

    ALLOW_MAXIMIZE = False

    def __init__(
        self,
        challenge: Challenge,
        index: int,
        total: int,
        logged_in: bool,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._ch = challenge
        self._index = index
        self._total = total
        self._logged_in = logged_in

    def compose(self) -> ComposeResult:
        at_start = self._index == 0
        at_end   = self._index == self._total - 1

        with Horizontal(id="nav-section"):
            yield Button(f"Problem List", id="btn-problem-list")
            yield Button(f"{_I_PREV}", id="btn-prev", disabled=at_start)
            yield Button(f"{_I_NEXT}", id="btn-next", disabled=at_end)

        with Horizontal(id="action-section"):
            yield Button(f"{_I_RUN} Run", id="btn-run")
            if self._logged_in:
                yield Button(f"{_I_SUBMIT} Submit", id="btn-submit")
                yield Button("Feedback", id="btn-feedback")

        with Horizontal(id="sol-section"):
            if self._ch.has_solutions:
                yield Button(f"Solution", id="btn-solution")


class _DetailBody(Horizontal):
    """Two-panel body: scrollable description (left) + editor and tabs (right)."""

    def __init__(self, challenge: Challenge, **kwargs) -> None:
        super().__init__(**kwargs)
        self._ch = challenge

    def compose(self) -> ComposeResult:
        ch = self._ch

        with Vertical(id="left-panel"):
            with VerticalScroll(id="left-scroll"):
                yield ChallengeCard(ch, id="challenge-card")

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
                    yield DataTable(id="testcase-table", show_cursor=False, zebra_stripes=True)
                with TabPane(f"{_I_CHART}  Test Result", id="tab-result"):
                    yield DataTable(id="result-table", show_cursor=False, zebra_stripes=True)
                with TabPane(f"{_I_BULB}  Solution Explanation", id="tab-solution-explanation"):
                    with VerticalScroll():
                        if ch.has_solutions:
                            yield Static(ch.solution_explanation or "", id="solution-explanation")
                        else:
                            yield Static(
                                "No solution available for this challenge.",
                                id="no-solution-msg",
                            )


class ChallengeDetailScreen(BaseScreen):
    """Full problem view: top bar, description panel, code editor, tabs."""

    BINDINGS = [
        Binding("escape",  "pop_screen",     "Problem List"),
        Binding("ctrl+q",  "quit_app",       "Exit LeetVibe"),
        Binding("ctrl+p",  "open_palette",   "Palette",       show=False),
        Binding("left",    "prev_challenge", "Prev",          show=False),
        Binding("right",   "next_challenge", "Next",          show=False),
        Binding("h",       "toggle_hints",   "Hints"),
        Binding("l",       "start_session",  "Learn with Mistral Vibe", show=False),
        Binding("p",       "start_session",  "Pair with Mistral Vibe",  show=False),
    ]

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
        self._logged_in = is_logged_in()
        self._cloud_session_id: str | None = None

    def compose(self) -> ComposeResult:
        yield _DetailTopBar(
            self._challenge,
            self._index,
            len(self._challenges),
            self._logged_in,
            id="top-bar",
        )
        yield _DetailBody(self._challenge, id="detail-body")
        if self._mode == "learn":
            session_hint = ("L", "Learn with Mistral Vibe", self.action_start_session, True)
        else:
            session_hint = ("P", "Pair with Mistral Vibe", self.action_start_session, True)
        yield StatusBar(
            hints=[
                session_hint,
                ("H",      "toggle hints", self.action_toggle_hints),
                ("Ctrl+P", "open palette", self.action_open_palette),
                ("Esc",    "go back",      self.action_pop_screen),
                ("Ctrl+Q", "Exit LeetVibe",self.action_quit_app),
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
            from ...cloud.auth import is_logged_in
            body = f"All {total} test case(s) passed! Saving solution…" if is_logged_in() else f"All {total} test case(s) passed!"
            self.notify(body, title="Accepted", severity="information")
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
        from ...cloud.auth import is_logged_in
        if not is_logged_in():
            return  # not signed in — skip cloud save silently
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

    def action_open_palette(self) -> None:
        self.call_later(self.app.action_command_palette)
