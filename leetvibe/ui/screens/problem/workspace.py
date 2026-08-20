"""ProblemWorkspaceScreen — LeetCode-style two-panel layout with custom top bar."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from rich.style import Style
from rich.text import Text as RichText

from textual.widgets import (
    Button,
    DataTable,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual.widgets.text_area import TextAreaTheme
from textual.worker import Worker, WorkerState

from leetvibe.problem_loader import Problem
from leetvibe.cloud.auth import is_logged_in
from leetvibe.code_runner import CaseResult, run_tests_with_timeout
from leetvibe.ui.widgets import ProblemCard, StatusBar
from leetvibe.ui.screens.base import BaseScreen

# ── Code editor theme — a builtin theme's real token colors (kept as-is,
# unmodified, for familiarity), re-backgrounded onto the app's own dark tone
# instead of the theme's native background. Only the background-tied fields
# are overridden; syntax_styles, the cursor block, bracket matching and
# selection colors are reused verbatim from the builtin theme. Swap
# _BASE_THEME_NAME to pick a different builtin palette (e.g. "monokai",
# "dracula") — the cursor-line shade is derived from it automatically, so
# nothing else here needs to change.
_BASE_THEME_NAME = "monokai"
_EDITOR_BG = "#161310"


def _rgb(color) -> tuple[int, int, int]:
    t = color.get_truecolor()
    return t.red, t.green, t.blue


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{max(0, min(255, c)):02x}" for c in rgb)


def _rebase_cursor_line(editor_bg: str, base_theme: TextAreaTheme) -> str:
    """Shade *editor_bg* the same way *base_theme* shades its own background
    for the cursor line, so the base->highlighted-line relationship holds
    regardless of which builtin theme (and its own bg tone) is chosen."""
    base_rgb = _rgb(base_theme.base_style.bgcolor)
    line_rgb = _rgb(base_theme.cursor_line_style.bgcolor)
    delta = tuple(line_c - base_c for line_c, base_c in zip(line_rgb, base_rgb))
    editor_rgb = tuple(int(editor_bg[i : i + 2], 16) for i in (1, 3, 5))
    return _hex(tuple(c + d for c, d in zip(editor_rgb, delta)))


_base_theme = TextAreaTheme.get_builtin_theme(_BASE_THEME_NAME)
assert _base_theme is not None
_EDITOR_LINE_BG = _rebase_cursor_line(_EDITOR_BG, _base_theme)

LEETVIBE_EDITOR_THEME = TextAreaTheme(
    name="leetvibe",
    base_style=Style(color=_base_theme.base_style.color, bgcolor=_EDITOR_BG),
    gutter_style=Style(color=_base_theme.gutter_style.color, bgcolor=_EDITOR_BG),
    cursor_style=_base_theme.cursor_style,
    cursor_line_style=Style(bgcolor=_EDITOR_LINE_BG),
    cursor_line_gutter_style=Style(
        color=_base_theme.cursor_line_gutter_style.color, bgcolor=_EDITOR_LINE_BG
    ),
    bracket_matching_style=_base_theme.bracket_matching_style,
    selection_style=_base_theme.selection_style,
    syntax_styles=_base_theme.syntax_styles,
)


class CodeEditor(TextArea):
    """TextArea with Ctrl+A remapped to select-all, plus indent-aware Enter,
    always themed with LeetVibe's brand palette regardless of the ``theme``
    kwarg passed at construction — a custom theme must be registered on the
    instance before it can be selected, so this can't just be a constructor
    default the way the builtin theme names are.

    Textual's TextArea has no auto-indent of any kind here — Enter is
    handled directly inside TextArea._on_key() (never routed through the
    actions/bindings system), which just inserts a bare "\\n". Intercepting
    it before that runs is the only hook point: carry the current line's
    leading whitespace onto the new line, and add one more indent level
    when the line up to the edit point ends with ':' (block openers).
    """

    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False, priority=True),
    ]

    def __init__(self, *args, **kwargs) -> None:
        kwargs.pop("theme", None)
        super().__init__(*args, **kwargs)
        self.register_theme(LEETVIBE_EDITOR_THEME)
        self.theme = "leetvibe"

    async def _on_key(self, event: Key) -> None:
        if event.key == "enter" and not self.read_only:
            event.stop()
            event.prevent_default()
            self._insert_smart_newline()
            return
        await super()._on_key(event)

    def _insert_smart_newline(self) -> None:
        start, end = self.selection
        row, col = start
        line = self.document.get_line(row)
        before = line[:col]
        indent = before[: len(before) - len(before.lstrip(" \t"))]
        if before.rstrip().endswith(":"):
            indent += "\t" if self.indent_type == "tabs" else " " * self.indent_width
        self.replace("\n" + indent, start, end)


# ── Defaults ───────────────────────────────────────────────────────────────────
_DEFAULT_PYTHON = "class Solution:\n    def solve(self):\n        pass\n"

# ── UI icons (standard Unicode — no Nerd Font required) ───────────────────────
_I_PREV   = "←"    # Prev
_I_NEXT   = "→"    # Next
_I_RUN    = "▶"    # Run
_I_SUBMIT = "↑"    # Submit

class _DetailTopBar(Horizontal):
    """Top navigation bar with nav, action and solution buttons."""

    ALLOW_MAXIMIZE = False

    def __init__(
        self,
        problem: Problem,
        index: int,
        total: int,
        logged_in: bool,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._ch = problem
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

    def __init__(self, problem: Problem, **kwargs) -> None:
        super().__init__(**kwargs)
        self._ch = problem

    def compose(self) -> ComposeResult:
        ch = self._ch

        with Vertical(id="left-panel"):
            with VerticalScroll(id="left-scroll"):
                yield ProblemCard(ch, id="problem-card")

        with Vertical(id="right-panel"):
            with Vertical(id="editor-panel"):
                yield CodeEditor(
                    ch.python_snippet or _DEFAULT_PYTHON,
                    language="python",
                    soft_wrap=False,
                    tab_behavior="indent",
                    show_line_numbers=True,
                    id="code-editor",
                )

            with TabbedContent(id="console-tabs"):
                with TabPane(f" Test Cases ", id="tab-test-cases"):
                    yield DataTable(id="test-cases-table", show_cursor=False, zebra_stripes=True)
                with TabPane(f" Test Results ", id="tab-test-results"):
                    yield DataTable(id="test-results-table", show_cursor=False, zebra_stripes=True)
                with TabPane(f" Solution Explanation ", id="tab-solution-explanation"):
                    with VerticalScroll():
                        if ch.has_solutions:
                            # Raw LeetCode solution text, never Rich-markup-templated —
                            # markup=False so a literal "[...]" in an example (e.g.
                            # equations = ["a!=b","b!=a"]) can't crash markup parsing.
                            yield Static(
                                ch.solution_explanation or "",
                                id="solution-explanation",
                                markup=False,
                            )
                        else:
                            yield Static(
                                "No solution available for this problem.",
                                id="no-solution-msg",
                            )


class ProblemWorkspaceScreen(BaseScreen):
    """Full problem view: top bar, description panel, code editor, tabs."""

    BINDINGS = [
        Binding("escape",        "pop_screen",          "Problem List"),
        Binding("ctrl+q",        "quit_app",            "Exit LeetVibe"),
        Binding("left",          "prev_problem",      "Prev",               show=False),
        Binding("right",         "next_problem",      "Next",               show=False),
        Binding("ctrl+g",        "toggle_hints",        "Hints"),
        Binding("ctrl+l",        "start_learn_session", "Learn with LeetVibe", show=False),
        Binding("ctrl+p",        "start_pair_session",  "Pair with LeetVibe",  show=False),
    ]

    def __init__(
        self,
        problem: Problem,
        problems: list[Problem],
        index: int,
        mode: str = "learn",
        drafts: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self._problem = problem
        self._problems = problems
        self._index = index
        self._mode = mode
        self._drafts: dict[str, str] = drafts if drafts is not None else {}
        self._solution_shown = False
        self._logged_in = is_logged_in()
        self._cloud_session_id = self._compute_session_id()

    def _compute_session_id(self) -> str | None:
        """Deterministic id of the AI chat session for this problem+mode.

        ProblemWorkspaceScreen never itself creates a chat_sessions doc — only
        AgentSessionScreen does, on demand — but the id is fully derivable
        from user_id + problem + mode without needing one to exist yet, so
        feedback submitted from the code editor still correlates correctly
        even before (or without) the user ever starting a Learn/Pair session
        on this problem. None when not signed in, matching every other
        cloud.db call's "no-op when logged out" contract.
        """
        if not self._logged_in:
            return None
        from leetvibe.cloud.auth import load_session
        from leetvibe.problem_loader import session_slug
        session = load_session()
        user_id = session.get("user_id") if session else None
        if not user_id:
            return None
        return f"{user_id}__{session_slug(self._problem)}__{self._mode}"

    def compose(self) -> ComposeResult:
        yield _DetailTopBar(
            self._problem,
            self._index,
            len(self._problems),
            self._logged_in,
            id="top-bar",
        )
        yield _DetailBody(self._problem, id="detail-body")
        hints = []
        if self._mode == "learn":
            hints.append(("Ctrl+L", "Learn with AI", self.action_start_learn_session, True))
        elif self._mode == "pair":
            hints.append(("Ctrl+P", "Pair with AI",  self.action_start_pair_session,  True))
        hints += [
            ("Ctrl+G",  "get hints",    self.action_toggle_hints),
            ("Ctrl+K",  "key commands", self.action_open_palette),
            ("Esc",     "go back",      self.action_pop_screen),
            ("Ctrl+Q",  "exit LeetVibe",self.action_quit_app),
        ]
        yield StatusBar(
            hints=hints,
            show_count=False,
            id="detail-status",
        )

    # ── Lifecycle ──────────────────────────────────────────────────────

    def on_mount(self) -> None:
        tabs = self.query_one("#console-tabs", TabbedContent)
        tabs.hide_tab("tab-solution-explanation")
        # No run has happened yet — an empty results table isn't worth a tab.
        tabs.hide_tab("tab-test-results")
        self._populate_testcase_table()
        self._setup_result_table()
        if not self._problem.hints:
            self.query_one("#detail-status", StatusBar).set_hint_visible(1, False)
        # Restore draft if one exists for this problem
        draft = self._drafts.get(self._problem.id)
        if draft is not None:
            self._load_editor(draft)

    # ── Helpers ────────────────────────────────────────────────────────

    def _populate_testcase_table(self) -> None:
        ch = self._problem
        table = self.query_one("#test-cases-table", DataTable)
        table.add_columns("#", "Input", "Expected Output")
        for i, inputs in enumerate(ch.test_cases[:5], 1):
            expected = ch.expected_outputs[i - 1] if i - 1 < len(ch.expected_outputs) else "—"
            input_str = "\n".join(str(v) for v in inputs)
            table.add_row(str(i), input_str, expected)

    def _setup_result_table(self) -> None:
        table = self.query_one("#test-results-table", DataTable)
        table.add_columns("#", "Input", "Expected", "Actual Output", "Status")

    def _reveal_results_tab(self) -> None:
        """Show and focus the Test Results tab — only called once it actually
        has content (a finished run's rows, or an error row). Hidden on mount
        and after a hide, since an empty table isn't worth a tab."""
        tabs = self.query_one("#console-tabs", TabbedContent)
        tabs.show_tab("tab-test-results")
        tabs.active = "tab-test-results"

    def _load_editor(self, code: str) -> None:
        self.query_one("#code-editor", TextArea).load_text(code)

    def _save_draft(self) -> None:
        """Persist current editor content to the shared drafts dict."""
        code = self.query_one("#code-editor", TextArea).text
        default = self._problem.python_snippet or _DEFAULT_PYTHON
        if code != default:
            self._drafts[self._problem.id] = code
        else:
            self._drafts.pop(self._problem.id, None)

    def _toggle_solution(self) -> None:
        ch = self._problem
        tabs = self.query_one("#console-tabs", TabbedContent)
        if self._solution_shown:
            tabs.hide_tab("tab-solution-explanation")
            self._load_editor(ch.python_snippet or _DEFAULT_PYTHON)
            self._solution_shown = False
        else:
            if not ch.has_solutions:
                self.notify(
                    "No solution available for this problem.",
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
            self._save_draft()
            self.app.switch_screen(
                ProblemWorkspaceScreen(
                    self._problems[self._index - 1],
                    self._problems,
                    self._index - 1,
                    self._mode,
                    self._drafts,
                )
            )

        elif btn == "btn-next" and self._index < len(self._problems) - 1:
            self._save_draft()
            self.app.switch_screen(
                ProblemWorkspaceScreen(
                    self._problems[self._index + 1],
                    self._problems,
                    self._index + 1,
                    self._mode,
                    self._drafts,
                )
            )

        elif btn == "btn-run":
            code = self.query_one("#code-editor", TextArea).text
            ch = self._problem
            snippet = ch.python_snippet or _DEFAULT_PYTHON
            self.query_one("#btn-run", Button).disabled = True
            self.query_one("#test-results-table", DataTable).clear()
            self._run_code(code, snippet, ch.test_cases, ch.expected_outputs)

        elif btn == "btn-submit":
            code = self.query_one("#code-editor", TextArea).text
            ch = self._problem
            snippet = ch.python_snippet or _DEFAULT_PYTHON
            self.query_one("#btn-submit", Button).disabled = True
            self._submit_code(code, snippet, ch.test_cases, ch.expected_outputs)

        elif btn == "btn-feedback":
            from leetvibe.ui.screens.feedback import FeedbackModal
            self.app.push_screen(
                FeedbackModal(
                    problem_slug=self._problem.id,
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
        return run_tests_with_timeout(code, snippet, test_cases, expected_outputs)

    @work(thread=True)
    def _submit_code(
        self,
        code: str,
        snippet: str,
        test_cases: list[list[str]],
        expected_outputs: list[str],
    ) -> list[CaseResult]:
        return run_tests_with_timeout(code, snippet, test_cases, expected_outputs)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "_run_code":
            self.query_one("#btn-run", Button).disabled = False
            if event.state == WorkerState.SUCCESS:
                self._display_results(event.worker.result or [])
            elif event.state == WorkerState.ERROR:
                table = self.query_one("#test-results-table", DataTable)
                table.clear()
                table.add_row("—", "—", "—", "—", RichText("Internal error", style="bold red"))
                self._reveal_results_tab()

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

        self._display_results(results)

        if passed == total:
            from leetvibe.cloud.auth import is_logged_in
            body = f"All {total} test case(s) passed! Saving solution…" if is_logged_in() else f"All {total} test case(s) passed!"
            self.notify(body, title="Accepted", severity="information")
            code = self.query_one("#code-editor", TextArea).text
            self._save_solution(code)
        else:
            self.notify(
                f"{passed}/{total} test case(s) passed. Keep going!",
                title="Wrong Answer",
                severity="warning",
            )

    @work(thread=True)
    def _save_solution(self, code: str) -> None:
        from leetvibe.cloud.auth import is_logged_in
        if not is_logged_in():
            return
        from leetvibe.cloud.db import mark_solved
        ch = self._problem
        ok = mark_solved(ch.id, ch.difficulty, code)
        self.app.call_from_thread(self._on_solution_saved, ok)


    def _on_solution_saved(self, ok: bool) -> None:
        if ok:
            self.notify("Solution saved to your profile!", title="Solved", severity="information")
            # Optimistically update the problem list screen so the solved badge
            # appears immediately without waiting for a Firestore re-read.
            from leetvibe.ui.screens.problem.list import ProblemListScreen
            for screen in self.app.screen_stack:
                if isinstance(screen, ProblemListScreen) and screen.is_mounted:
                    if screen._solved_slugs is None:
                        screen._solved_slugs = set()
                    screen._solved_slugs = screen._solved_slugs | {self._problem.id}
                    if screen._all_problems:
                        screen._repopulate()
                    break
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
        table = self.query_one("#test-results-table", DataTable)
        table.clear()
        for r in results:
            input_str = ",  ".join(self._fmt_value(v) for v in r.inputs) if r.inputs else "—"
            expected = r.expected or "—"
            if r.error:
                actual = RichText(r.error, style="red")
                status = RichText("Error", style="bold red")
            else:
                actual = RichText(self._fmt_value(r.output), style="white")
                if r.passed is True:
                    status = RichText("Pass", style="bold #00C44F")
                elif r.passed is False:
                    status = RichText("Fail", style="bold yellow")
                else:
                    status = RichText("—", style="dim")
            table.add_row(str(r.case_num), input_str, expected, actual, status)
        self._reveal_results_tab()

    # ── Actions ────────────────────────────────────────────────────────

    def action_pop_screen(self) -> None:
        self._save_draft()
        self.app.pop_screen()

    def action_toggle_hints(self) -> None:
        self.query_one("#problem-card", ProblemCard).show_hints ^= True

    def action_start_learn_session(self) -> None:
        if self._mode != "learn":
            return
        from leetvibe.ui.screens.agent.session import AgentSessionScreen
        user_code = self.query_one("#code-editor", TextArea).text
        self.app.push_screen(
            AgentSessionScreen(self._problem, mode="learn", user_code=user_code)
        )

    def action_start_pair_session(self) -> None:
        if self._mode != "pair":
            return
        from leetvibe.ui.screens.agent.session import AgentSessionScreen
        user_code = self.query_one("#code-editor", TextArea).text
        self.app.push_screen(
            AgentSessionScreen(self._problem, mode="pair", user_code=user_code)
        )

    def action_prev_problem(self) -> None:
        if self._index > 0:
            self._save_draft()
            self.app.switch_screen(
                ProblemWorkspaceScreen(
                    self._problems[self._index - 1],
                    self._problems,
                    self._index - 1,
                    self._mode,
                    self._drafts,
                )
            )

    def action_next_problem(self) -> None:
        if self._index < len(self._problems) - 1:
            self._save_draft()
            self.app.switch_screen(
                ProblemWorkspaceScreen(
                    self._problems[self._index + 1],
                    self._problems,
                    self._index + 1,
                    self._mode,
                    self._drafts,
                )
            )

    def action_open_palette(self) -> None:
        self.call_later(self.app.action_command_palette)
