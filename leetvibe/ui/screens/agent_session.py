"""AgentSessionScreen — mistral-vibe style chat layout for AI sessions."""

from __future__ import annotations

import os
import re
import threading

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalGroup, VerticalScroll
from textual.widgets import Button, Input, Static

from ...problem_loader import Problem
from ..theme import FIRE, GRADIENT, GREEN, RED, SHIMMER
from ..widgets.problem_card import ProblemCard
from ..widgets.status_bar import StatusBar
from .base import BaseScreen

# Strip Rich markup tags like [bold], [/dim], [#FF0000] before regex matching
_MARKUP_RE = re.compile(r"\[/?[^\]]*\]")
# Strip markdown bold (**text**) and heading (### text) markers before matching
_MD_DECORATION_RE = re.compile(r"^[*#\s]+|[*#\s]+$")
# Matches "STEP N — Title", "STEP N - Title", "STEP N: Title" (case-insensitive)
# Works whether or not the line is wrapped in **…** or ### …
_STEP_RE = re.compile(r"^\s*STEP\s+(\d+)\s*[—–\-:]+\s*(.*)", re.IGNORECASE)
# Matches standalone "Call toolname(...)" lines emitted by the LLM before tool dispatch
_TOOL_CALL_LINE_RE = re.compile(r"^Call\s+\w+\s*\(.*\)\s*$", re.IGNORECASE)

# ── Markdown → Rich markup ─────────────────────────────────────────────────────
_MD_FENCE_RE = re.compile(r"^```(\w*)")
_MD_HEADING_RE = re.compile(r"^#{1,3}\s+(.*)")
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_MD_HR_RE = re.compile(r"^[-]{3,}$")


def _md_to_rich(line: str, in_code_block: bool) -> tuple[str, bool]:
    """Convert one streamed Markdown line to Rich markup.

    Returns (rendered_line, new_in_code_block). Handles:
      - ``` fences → dim language label / closing blank line
      - Code block content → escaped so Rich doesn't mis-parse brackets
      - ### headings → bold fire-orange
      - **bold** → [bold]…[/bold]
      - `inline code` → fire-orange
      - --- → dim horizontal rule
    """
    stripped = line.strip()

    # Code fence open/close
    fence_m = _MD_FENCE_RE.match(stripped)
    if fence_m:
        if in_code_block:
            return "", False
        lang = fence_m.group(1) or "code"
        dashes = "─" * max(0, 14 - len(lang))
        return f"[dim]─── {lang} {dashes}[/dim]", True

    if in_code_block:
        # Escape [ so Rich doesn't try to parse code as markup
        return line.replace("[", r"\["), True

    # Horizontal rule — suppress (LLM-emitted --- adds visual noise before steps)
    if _MD_HR_RE.match(stripped):
        return "", False

    # Headings (# / ## / ###) → bold fire-orange, prefixed with blank line
    h = _MD_HEADING_RE.match(stripped)
    if h:
        title = _MD_BOLD_RE.sub(r"\1", h.group(1).strip())
        return f"\n[bold #FF8205]{title}[/bold #FF8205]", False

    # Inline: **bold** and `code`
    line = _MD_BOLD_RE.sub(r"[bold]\1[/bold]", line)
    line = _MD_INLINE_CODE_RE.sub(r"[#FF8205]\1[/#FF8205]", line)
    return line, False

# ── Chat widgets ───────────────────────────────────────────────────────────────


class ChatScroll(VerticalScroll):
    """Performance-optimised scroll container — skips cascading style recalcs."""

    def update_node_styles(self, animate: bool = True) -> None:  # noqa: FBT001
        pass


class UserMessage(Static):
    """User / problem turn: orange heavy left-border bubble."""

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def compose(self) -> ComposeResult:
        yield Static(self._text, markup=True, classes="msg-content")


class CopyableCodeBlock(Static):
    """Inline code block with a one-click ⎘ copy button."""

    def __init__(self, lang: str) -> None:
        super().__init__()
        self._lang = lang or "code"
        self._lines: list[str] = []
        self._body: Static | None = None
        self._btn: Button | None = None

    def compose(self) -> ComposeResult:
        dashes = "─" * max(0, 14 - len(self._lang))
        with Horizontal(classes="cb-header"):
            yield Static(
                f"[dim]─── {self._lang} {dashes}[/dim]",
                markup=True, classes="cb-lang",
            )
            self._btn = Button("⎘", classes="cb-btn")
            yield self._btn
        self._body = Static("", markup=False, classes="cb-body")
        yield self._body

    def add_line(self, line: str) -> None:
        self._lines.append(line)
        if self._body is not None:
            try:
                self._body.update("\n".join(self._lines))
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.copy_to_clipboard("\n".join(self._lines))
        event.stop()
        if self._btn is not None:
            self._btn.label = "✓"
            self.set_timer(1.5, self._reset_btn)

    def _reset_btn(self) -> None:
        if self._btn is not None:
            self._btn.label = "⎘"


def _write_line_to_container(
    line: str,
    container: "VerticalGroup",
    text_lines: list[str],
    text_widget_ref: list["Static | None"],
    code_block_ref: list["CopyableCodeBlock | None"],
    in_code_block_ref: list[bool],
) -> None:
    """Shared logic: route a streamed line into a VerticalGroup as text or code widget."""
    stripped = line.strip()
    fence_m = _MD_FENCE_RE.match(stripped)

    if fence_m:
        if in_code_block_ref[0]:
            # Close code block — start a fresh text segment
            in_code_block_ref[0] = False
            code_block_ref[0] = None
            new_text = Static("", markup=True, classes="step-text")
            text_widget_ref[0] = new_text
            text_lines.clear()
            try:
                container.mount(new_text)
            except Exception:
                pass
        else:
            # Open code block
            lang = fence_m.group(1) or "code"
            in_code_block_ref[0] = True
            cb = CopyableCodeBlock(lang)
            code_block_ref[0] = cb
            try:
                container.mount(cb)
            except Exception:
                pass
        return

    if in_code_block_ref[0]:
        if code_block_ref[0] is not None:
            code_block_ref[0].add_line(line)
    else:
        rendered, _ = _md_to_rich(line, False)
        text_lines.append(rendered)
        tw = text_widget_ref[0]
        if tw is not None:
            try:
                tw.update("\n".join(text_lines))
            except Exception:
                pass


class BackgroundStep(Static):
    """Steps 1-7 and 9+: shimmer spinner header + collapsible content (hidden by default)."""

    SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, step_num: int, title: str, content_visible: bool = False) -> None:
        super().__init__()
        self._step_num = step_num
        self._title = title
        self._tick = 0
        self._done = False
        self._done_color: str = GRADIENT[0]
        self._content_visible = content_visible
        self._header_widget: Static | None = None
        self._content_container: VerticalGroup | None = None
        # Mutable refs passed to the shared write helper
        self._text_lines: list[str] = []
        self._text_widget_ref: list[Static | None] = [None]
        self._code_block_ref: list[CopyableCodeBlock | None] = [None]
        self._in_code_block_ref: list[bool] = [False]

    def compose(self) -> ComposeResult:
        self._header_widget = Static(self._render_header(), markup=True, classes="step-header")
        yield self._header_widget
        self._content_container = VerticalGroup(classes="step-content")
        yield self._content_container

    def on_mount(self) -> None:
        if self._content_container is not None:
            self._content_container.display = self._content_visible
            init_text = Static("", markup=True, classes="step-text")
            self._text_widget_ref[0] = init_text
            self._content_container.mount(init_text)

    def _shimmer_text(self, text: str) -> str:
        parts: list[str] = []
        n = len(SHIMMER)
        for i, ch in enumerate(text):
            color = SHIMMER[(self._tick + i) % n]
            safe = ch.replace("[", r"\[")
            parts.append(f"[bold {color}]{safe}[/bold {color}]")
        return "".join(parts)

    def _render_header(self) -> str:
        if self._done:
            color = self._done_color
            icon = f"[bold {color}]✓[/bold {color}]"
            return f"{icon} [{color}]Step {self._step_num} — {self._title}[/{color}]"
        spinner_ch = self.SPINNER[self._tick % len(self.SPINNER)]
        return self._shimmer_text(f"{spinner_ch} Step {self._step_num} — {self._title}")

    def advance_spinner(self) -> None:
        if not self._done:
            self._tick += 1
            if self._header_widget is not None:
                try:
                    self._header_widget.update(self._render_header())
                except Exception:
                    pass

    def mark_done(self) -> None:
        self._done = True
        self._done_color = GRADIENT[(self._step_num - 1) % len(GRADIENT)]
        if self._header_widget is not None:
            try:
                self._header_widget.update(self._render_header())
            except Exception:
                pass

    def write_line(self, line: str) -> None:
        if self._content_container is None:
            return
        _write_line_to_container(
            line, self._content_container,
            self._text_lines, self._text_widget_ref,
            self._code_block_ref, self._in_code_block_ref,
        )

    def toggle_content(self, visible: bool) -> None:
        self._content_visible = visible
        if self._content_container is not None:
            self._content_container.display = visible


class FinalAnswer(Static):
    """Final synthesis step: always fully visible, supports copyable code blocks."""

    def __init__(self, step_num: int, title: str) -> None:
        super().__init__()
        self._step_num = step_num
        self._title = title
        self._content_container: VerticalGroup | None = None
        self._all_lines: list[str] = []   # raw lines kept for narration
        self._text_lines: list[str] = []
        self._text_widget_ref: list[Static | None] = [None]
        self._code_block_ref: list[CopyableCodeBlock | None] = [None]
        self._in_code_block_ref: list[bool] = [False]

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {FIRE}]━━  Step {self._step_num} — {self._title}  ━━[/bold {FIRE}]",
            markup=True,
            classes="final-sep",
        )
        self._content_container = VerticalGroup(classes="final-content")
        yield self._content_container

    def on_mount(self) -> None:
        if self._content_container is not None:
            init_text = Static("", markup=True, classes="step-text")
            self._text_widget_ref[0] = init_text
            self._content_container.mount(init_text)

    def write_line(self, line: str) -> None:
        self._all_lines.append(line)
        if self._content_container is None:
            return
        _write_line_to_container(
            line, self._content_container,
            self._text_lines, self._text_widget_ref,
            self._code_block_ref, self._in_code_block_ref,
        )


class AssistantBlock(Static):
    """One follow-up AI turn (or fallback block): accumulates streamed Rich-markup lines."""

    def __init__(self) -> None:
        super().__init__()
        self._lines: list[str] = []
        self._in_code_block = False
        self._display: Static | None = None

    def compose(self) -> ComposeResult:
        self._display = Static("", markup=True)
        yield self._display

    def on_mount(self) -> None:
        # Flush any lines that arrived before compose() ran
        if self._lines and self._display is not None:
            self._display.update("\n".join(self._lines))

    def write_line(self, line: str) -> None:
        rendered, self._in_code_block = _md_to_rich(line, self._in_code_block)
        self._lines.append(rendered)
        if self._display is not None:
            try:
                self._display.update("\n".join(self._lines))
            except Exception:
                pass


# ── Screen ─────────────────────────────────────────────────────────────────────


class AgentSessionScreen(BaseScreen):
    """Full-screen AI session with step-aware rendering and follow-up chat."""

    BINDINGS = [
        Binding("escape",  "pop_screen",          "← Back"),
        Binding("ctrl+s",  "stop_agent",          "■ Stop",        show=False),
        Binding("ctrl+h",  "toggle_history",      "Prior Session", show=False),
        Binding("ctrl+t",  "toggle_steps",        "Toggle Steps",  show=False),
        Binding("ctrl+d",  "toggle_description",  "Problem",       show=False, priority=True),
        Binding("ctrl+q",  "quit_app",            "Quit",          show=False),
    ]

    def __init__(
        self,
        problem: Problem,
        mode: str = "learn",
        user_code: str = "",
    ) -> None:
        super().__init__()
        self._problem = problem
        self._mode = mode
        self._user_code = user_code
        self._running = False
        self._line_buffer = ""
        self._agent = None
        self._concept_agent: "ConceptAgent | None" = None
        self._session_summary: dict = {}
        self._chat_running = False
        self._current_block: AssistantBlock | None = None
        # Step-mode state (initial session only)
        self._step_mode = False
        self._is_final = False
        self._steps_visible = False
        self._current_step: BackgroundStep | None = None
        self._current_final: FinalAnswer | None = None
        self._spinner_timer = None   # Timer | None
        self._session_done = False   # guard against double _on_agent_done
        self._cloud_session_id: str | None = None  # set once by _run_agent
        self._prior_messages: list[dict] = []      # saved messages from last session
        self._history_visible = False              # Ctrl+O toggle state

    # ── Layout ────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        ch = self._problem
        diff_color = {"easy": GREEN, "medium": "#FFB300", "hard": RED}.get(
            ch.difficulty.lower(), "#888888"
        )

        with Horizontal(id="session-bar"):
            yield Button("← Back", id="btn-back")
            yield Static(
                f"[{diff_color}]{ch.title}[/{diff_color}]"
                f"  [dim]({ch.difficulty})[/dim]",
                id="session-title",
            )
            yield Button("⎘ Copy Code", id="btn-copy", disabled=True)
            yield Button("↺ Reset", id="btn-reset")
            yield Button("■ Stop", id="btn-stop")

        with Horizontal(id="session-body"):
            with VerticalScroll(id="description-panel"):
                yield ProblemCard(ch)
                yield Static("", id="interview-opening", markup=True)
            with ChatScroll(id="chat-scroll"):
                with VerticalGroup(id="prior-history"):
                    yield Static(
                        "── Prior session ──────────────────────",
                        id="prior-history-title",
                    )
                yield VerticalGroup(id="messages")

        with Vertical(id="chat-input-container"):
            with Horizontal(id="input-box"):
                yield Input(
                    placeholder="Session in progress…",
                    id="chat-input",
                    disabled=True,
                )
                yield Button("Send", id="btn-send", disabled=True)

        yield StatusBar(
            hints=[
                ("Ctrl+D", "see problem description",         self.action_toggle_description),  # 0 — interview only
                ("Ctrl+S", "stop agent",      self.action_stop_agent),           # 1
                ("Ctrl+T", "toggle steps",    self.action_toggle_steps),         # 2 — hidden in interview
                ("Ctrl+H", "view history",    self.action_toggle_history),       # 3 — hidden until history exists
                ("Esc",    "go back",         self.action_pop_screen),           # 4
                ("Ctrl+Q", "quit",            self.action_quit_app),             # 5
            ],
            show_count=False,
            id="session-status",
        )

    # ── Lifecycle ─────────────────────────────────────────────────────

    def on_mount(self) -> None:
        ch = self._problem
        diff_color = {"easy": GREEN, "medium": "#FFB300", "hard": RED}.get(
            ch.difficulty.lower(), "#888888"
        )
        from ..widgets.status_bar import StatusBar
        status = self.query_one("#session-status", StatusBar)
        # Ctrl+H (index 3) is hidden until prior history is confirmed
        status.set_hint_visible(3, False)
        if self._mode == "interview":
            # No opening label — Alex's greeting is the first thing the user should see
            # Hide learn-mode-only hints and irrelevant header buttons
            status.set_hint_visible(0, True)   # Ctrl+D — problem
            status.set_hint_visible(2, False)  # Ctrl+T — toggle steps
            try:
                self.query_one("#btn-copy", Button).display = False
                self.query_one("#btn-reset", Button).display = False
            except Exception:
                pass
        else:
            # Non-interview: show opening label, hide Ctrl+D
            label = (
                f"[dim]Mode: {self._mode.title()}[/dim]  ·  "
                f"[{diff_color}]{ch.title}[/{diff_color}]  "
                f"[dim]({ch.difficulty})[/dim]"
            )
            self._mount_user_message(label)
            status.set_hint_visible(0, False)  # Ctrl+D
        self._spinner_timer = self.set_interval(0.1, self._tick_spinner)
        self._running = True
        # Interview mode has no numbered steps — use plain AssistantBlock throughout
        self._step_mode = self._mode != "interview"
        self._run_agent(self._problem, self._mode, self._user_code)

    def on_unmount(self) -> None:
        """Stop any in-progress audio when the screen is closed."""
        try:
            from ...ai.skills.voice_narrator.server import stop_playback
            stop_playback()
        except Exception:
            pass

    # ── Message mounting ───────────────────────────────────────────────

    def _mount_user_message(self, text: str) -> None:
        msg = UserMessage(text)
        self.query_one("#messages", VerticalGroup).mount(msg)
        self._scroll_to_bottom()

    def _mount_assistant_block(self) -> None:
        block = AssistantBlock()
        self._current_block = block
        self.query_one("#messages", VerticalGroup).mount(block)

    def _scroll_to_bottom(self) -> None:
        self.query_one("#chat-scroll", ChatScroll).scroll_end(animate=False)

    # ── Spinner ────────────────────────────────────────────────────────

    def _tick_spinner(self) -> None:
        if self._current_step is not None:
            self._current_step.advance_spinner()

    # ── Step routing ───────────────────────────────────────────────────

    def _start_new_step(self, step_num: int, title: str) -> None:
        """Mount a new step widget and mark the previous one as done."""
        if self._current_step is not None:
            self._current_step.mark_done()
            self._current_step = None

        if step_num == 8:
            self._is_final = True
            final = FinalAnswer(step_num, title)
            self._current_final = final
            self.query_one("#messages", VerticalGroup).mount(final)
        else:
            self._is_final = False
            step = BackgroundStep(step_num, title, content_visible=self._steps_visible)
            self._current_step = step
            self.query_one("#messages", VerticalGroup).mount(step)

        self._scroll_to_bottom()

    # ── Worker ────────────────────────────────────────────────────────

    @work(thread=True)
    def _run_agent(self, problem: Problem, mode: str, user_code: str) -> None:
        """Background thread: streams agent output into step widgets."""
        from ...session_log import SessionLog
        from ...cloud.db import load_messages, save_messages, upsert_session

        session_log = SessionLog(problem, mode, user_code)
        error_msg: str | None = None

        problem_slug = getattr(problem, "title_slug", None) or problem.title

        try:
            from ...config import load_config
            config = load_config()

            self._cloud_session_id = upsert_session(
                problem_slug, problem.difficulty, mode
            )

            if mode == "interview":
                from ...ai.agent import InterviewAgent
                self._agent = InterviewAgent(config)
                for chunk in self._agent.start_streaming(problem):
                    if not self._running:
                        break
                    session_log.record_chunk(chunk)
                    self.app.call_from_thread(self._buffer_chunk, chunk)
                self.app.call_from_thread(self._flush_buffer)
            else:
                from ...ai.agent import VibeAgent, COACH_PROMPT, SYSTEM_PROMPT
                self._agent = VibeAgent(config)
                prior_messages = (
                    load_messages(problem_slug, mode)
                    if self._cloud_session_id
                    else []
                )
                if prior_messages:
                    system = (
                        COACH_PROMPT if mode == "coach" and user_code.strip()
                        else SYSTEM_PROMPT
                    )
                    self._agent.inject_history(
                        [{"role": "system", "content": system}, *prior_messages]
                    )
                    self._prior_messages = prior_messages
                    self.app.call_from_thread(self._render_prior_history, prior_messages)
                    self.app.call_from_thread(
                        self._write_line,
                        "[dim]📎  Resumed from last session — "
                        "press Ctrl+H to view prior conversation.[/dim]",
                    )
                else:
                    for chunk in self._agent.solve_streaming(problem, mode, user_code):
                        if not self._running:
                            break
                        session_log.record_chunk(chunk)
                        self.app.call_from_thread(self._buffer_chunk, chunk)
                    self.app.call_from_thread(self._flush_buffer)

        except Exception as exc:
            error_msg = str(exc)
            safe = error_msg.replace("[", r"\[").replace("\n", " ")
            self.app.call_from_thread(
                self._write_line, f"[bold red]Fatal error: {safe}[/bold red]"
            )
        finally:
            session_log.finish(error=error_msg)
            if self._cloud_session_id and self._agent is not None:
                save_messages(self._cloud_session_id, self._agent._messages)
            self.app.call_from_thread(self._on_agent_done)

    # ── Prior history rendering ───────────────────────────────────────

    def _render_prior_history(self, messages: list[dict]) -> None:
        """Populate the #prior-history container with saved messages."""
        from ..widgets.status_bar import StatusBar
        if self._mode != "interview":
            self.query_one("#session-status", StatusBar).set_hint_visible(3, True)
        container = self.query_one("#prior-history", VerticalGroup)
        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content") or "").strip()
            if not content:
                continue
            if role == "user":
                safe = content.replace("[", r"\[")
                container.mount(UserMessage(safe))
            elif role == "assistant":
                block = AssistantBlock()
                container.mount(block)
                for line in content.splitlines():
                    block.write_line(line)

    # ── Thread-safe UI helpers ────────────────────────────────────────

    def _buffer_chunk(self, chunk: str) -> None:
        """Accumulate streaming chunks; write complete lines to current widget."""
        self._line_buffer += chunk
        while "\n" in self._line_buffer:
            line, self._line_buffer = self._line_buffer.split("\n", 1)
            self._write_line(line)

    def _flush_buffer(self) -> None:
        if self._line_buffer:
            self._write_line(self._line_buffer)
            self._line_buffer = ""

    def _write_line(self, line: str) -> None:
        if self._step_mode:
            # Strip Rich markup then markdown bold/heading decorators before matching
            clean = _MARKUP_RE.sub("", line).strip()
            clean = _MD_DECORATION_RE.sub("", clean).strip()
            m = _STEP_RE.match(clean)
            if m:
                self._start_new_step(int(m.group(1)), m.group(2).strip())
                return
            # Suppress bare "Call toolname()" annotations — the tool block renders the name
            if _TOOL_CALL_LINE_RE.match(clean):
                return
            # Route content to the currently active widget
            if self._is_final and self._current_final is not None:
                self._current_final.write_line(line)
            elif self._current_step is not None:
                self._current_step.write_line(line)
            else:
                # No step detected yet — show content in a plain fallback block
                # so nothing is ever silently discarded
                if self._current_block is None:
                    self._mount_assistant_block()
                if self._current_block is not None:
                    self._current_block.write_line(line)
        else:
            # Non-step mode (interview / follow-up chat): plain AssistantBlock
            # Auto-create a block if none exists (interview initial session)
            if self._current_block is None:
                self._mount_assistant_block()
            if self._current_block is not None:
                self._current_block.write_line(line)
        self._scroll_to_bottom()

    def _on_agent_done(self) -> None:
        if self._session_done:
            return
        self._session_done = True
        self._running = False
        self._step_mode = False

        # Stop spinner
        if self._spinner_timer is not None:
            self._spinner_timer.stop()
            self._spinner_timer = None

        # Mark last background step complete
        if self._current_step is not None:
            self._current_step.mark_done()
            self._current_step = None

        if self._mode == "interview":
            # Narrate the AI's initial greeting (the problem intro + question)
            if self._current_block is not None:
                lines = list(self._current_block._lines)
                threading.Thread(
                    target=self._narrate_interview_turn,
                    args=(lines,),
                    daemon=True,
                ).start()
                # Populate the description panel with Alex's opening so the
                # user can always reference it via Ctrl+D
                opening_text = "\n".join(lines)
                try:
                    widget = self.query_one("#interview-opening", Static)
                    widget.update(
                        f"[dim]━━  Alex's opening  ━━[/dim]\n\n{opening_text}"
                    )
                except Exception:
                    pass
        else:
            # Extract step 7 text now while _current_final is still in scope
            step7_text = ""
            if self._current_final is not None:
                step7_text = self._extract_narration_text(self._current_final._all_lines)
            pattern = self._extract_algorithm_pattern(self._agent) if self._agent else ""
            log_data = self._extract_log_session_data(self._agent) if self._agent else {}
            self._session_summary = {
                "title": self._problem.title,
                "difficulty": self._problem.difficulty,
                "topics": self._problem.topics or [],
                "algorithm_pattern": pattern,
                "synthesis": step7_text,
                "complexity": log_data.get("final_complexity", ""),
            }
            self._trigger_mnemonic()

        # Append session-complete separator (not in interview — session stays open for chat)
        if self._mode != "interview":
            if self._current_final is not None:
                self._current_final.write_line("")
                self._current_final.write_line(f"[bold {FIRE}]━━  Session complete  ━━[/bold {FIRE}]")
            elif self._current_block is not None:
                self._current_block.write_line("")
                self._current_block.write_line(f"[bold {FIRE}]━━  Session complete  ━━[/bold {FIRE}]")

        self.query_one("#btn-stop", Button).disabled = True
        self.query_one("#btn-copy", Button).disabled = False
        inp = self.query_one("#chat-input", Input)
        inp.placeholder = "Ask a follow-up question…"
        self._set_chat_busy(False)

    # ── Step 7 text extraction ────────────────────────────────────────

    @staticmethod
    def _extract_narration_text(lines: list[str]) -> str:
        """Clean step-7 lines into plain prose suitable for TTS."""
        # Patterns to skip: tool-call spinner and result lines
        _SKIP_RE = re.compile(r"^\s*[⚙→]|Calling \w+|⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏")
        _BACKTICK_RE = re.compile(r"`[^`]*`")

        clean_lines = []
        for line in lines:
            plain = _MARKUP_RE.sub("", line).strip()
            if not plain or _SKIP_RE.search(plain):
                continue
            plain = _BACKTICK_RE.sub("", plain).strip()
            if plain:
                clean_lines.append(plain)

        return " ".join(clean_lines).strip()

    # ── Post-session mnemonic ─────────────────────────────────────────

    def _trigger_mnemonic(self) -> None:
        """Generate and append the algorithm mnemonic inline after the session."""
        if self._agent is None:
            return
        threading.Thread(
            target=self._post_session_worker,
            args=(self, self._agent),
            daemon=True,
        ).start()

    @staticmethod
    def _post_session_worker(screen: "AgentSessionScreen", agent: object) -> None:
        """Fetch the mnemonic and append it as a dim line to the final step."""
        try:
            pattern = AgentSessionScreen._extract_algorithm_pattern(agent)
            if not pattern:
                return
            mnemonic = AgentSessionScreen._get_or_generate_mnemonic(pattern)
            if mnemonic:
                line = f"\n[dim]Mnemonic:[/dim] {mnemonic}"
                screen.app.call_from_thread(screen._append_mnemonic, line)
        except Exception:
            pass

    def _append_mnemonic(self, line: str) -> None:
        if self._current_final is not None:
            self._current_final.write_line(line)
        elif self._current_block is not None:
            self._current_block.write_line(line)
        self._scroll_to_bottom()

    @staticmethod
    def _extract_algorithm_pattern(agent: object) -> str:
        """Find algorithm_pattern from the explain_approach tool call."""
        import json
        for msg in getattr(agent, "_messages", []):
            if msg.get("role") == "assistant":
                for tc in (msg.get("tool_calls") or []):
                    fn = tc.get("function", {})
                    if fn.get("name") == "explain_approach":
                        try:
                            args = json.loads(fn.get("arguments", "{}"))
                            return args.get("algorithm_pattern", "")
                        except Exception:
                            pass
        return ""

    @staticmethod
    def _get_or_generate_mnemonic(pattern: str) -> str:
        """Return cached mnemonic for pattern, or generate and cache a new one."""
        import json
        from pathlib import Path
        mnemonics_path = Path.home() / ".leetvibe" / "mnemonics.json"

        cache: dict = {}
        if mnemonics_path.exists():
            try:
                cache = json.loads(mnemonics_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        key = pattern.lower().strip()
        if key in cache:
            return cache[key]

        mnemonic = AgentSessionScreen._generate_mnemonic(key)
        if mnemonic:
            cache[key] = mnemonic
            try:
                mnemonics_path.parent.mkdir(parents=True, exist_ok=True)
                mnemonics_path.write_text(
                    json.dumps(cache, indent=2), encoding="utf-8"
                )
            except Exception:
                pass
        return mnemonic

    @staticmethod
    def _generate_mnemonic(pattern: str) -> str:
        """Call Mistral for a vivid 1-sentence analogy for the algorithm pattern."""
        try:
            from mistralai import Mistral
            resp = Mistral(api_key=os.environ.get("MISTRAL_API_KEY", "")).chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You write 1-sentence memory tricks for algorithm patterns. "
                            "The analogy MUST describe the algorithm's exact mechanical action "
                            "(how it moves through data, what it tracks, how it decides). "
                            "Be specific to this pattern — generic analogies are forbidden. "
                            "25 words max. No markdown, no quotes, no emojis."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Algorithm pattern: {pattern}\n"
                            f"Write an analogy that captures exactly HOW this algorithm works mechanically."
                        ),
                    },
                ],
                max_tokens=60,
            )
            return resp.choices[0].message.content.strip().strip("'")
        except Exception:
            return ""


    @staticmethod
    def _extract_log_session_data(agent: object) -> dict:
        """Infer session stats from tool calls — run_code count, complexity result."""
        import json
        import time as _time
        messages = getattr(agent, "_messages", [])
        approaches = 0
        complexity = ""

        for msg in messages:
            if msg.get("role") == "assistant":
                for tc in (msg.get("tool_calls") or []):
                    if tc.get("function", {}).get("name") == "run_code":
                        approaches += 1
            elif msg.get("role") == "tool":
                content = str(msg.get("content", ""))
                if not complexity:
                    try:
                        data = json.loads(content)
                        tc_val = data.get("time_complexity", "")
                        sc_val = data.get("space_complexity", "")
                        if tc_val and sc_val:
                            complexity = f"{tc_val} time, {sc_val} space"
                    except Exception:
                        pass

        start_ts = getattr(agent, "_start_ts", 0.0)
        time_s = int(_time.time() - start_ts) if start_ts else 0

        return {
            "approaches_tried": max(approaches, 1),
            "final_complexity": complexity,
            "time_seconds": time_s,
            "solved": True,
        }

    # ── Interview mode narration ──────────────────────────────────────

    def _flush_and_narrate_interview(self) -> None:
        """Flush buffer then queue narration of the AI's response (interview mode)."""
        self._flush_buffer()
        if self._current_block is None:
            return
        lines = list(self._current_block._lines)
        threading.Thread(
            target=self._narrate_interview_turn,
            args=(lines,),
            daemon=True,
        ).start()

    @staticmethod
    def _narrate_interview_turn(lines: list[str]) -> None:
        """Extract 1-2 sentences from the AI response and narrate with coach voice."""
        text = AgentSessionScreen._extract_interview_snippet(lines)
        if not text:
            return
        try:
            from ...ai.skills.voice_narrator.server import narrate
            narrate(text, voice_type="coach")
        except Exception:
            pass

    @staticmethod
    def _extract_interview_snippet(lines: list[str]) -> str:
        """Return the full AI interview response, clean of markup."""
        clean = []
        for line in lines:
            plain = _MARKUP_RE.sub("", line).strip()
            if plain and not plain.startswith(("⚙", "→", "⠋", "⠙", "⠹")):
                clean.append(plain)
        return " ".join(clean).strip()

    # ── Chat follow-up ────────────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat-input":
            self._submit_chat()

    def _submit_chat(self) -> None:
        if self._agent is None or self._chat_running:
            return
        inp = self.query_one("#chat-input", Input)
        text = inp.value.strip()
        if not text:
            return
        inp.value = ""
        self._run_chat(text)

    @work(thread=True)
    def _run_chat(self, user_message: str) -> None:
        from ...cloud.db import save_messages

        self._chat_running = True
        self.app.call_from_thread(self._set_chat_busy, True)
        safe_msg = user_message.replace("[", r"\[")
        self.app.call_from_thread(self._mount_user_message, safe_msg)
        self.app.call_from_thread(self._mount_assistant_block)
        try:
            if self._mode == "interview":
                agent = self._agent
            else:
                if self._concept_agent is None:
                    from ...ai.agent import ConceptAgent
                    from ...config import load_config
                    self._concept_agent = ConceptAgent(load_config(), self._session_summary)
                agent = self._concept_agent

            if agent is not None:
                for chunk in agent.chat_streaming(user_message):
                    self.app.call_from_thread(self._buffer_chunk, chunk)
            if self._mode == "interview":
                self.app.call_from_thread(self._flush_and_narrate_interview)
            else:
                self.app.call_from_thread(self._flush_buffer)
        except Exception as exc:
            safe = str(exc).replace("[", r"\[").replace("\n", " ")
            self.app.call_from_thread(
                self._write_line, f"[bold red]Error: {safe}[/bold red]"
            )
        finally:
            self._chat_running = False
            if self._mode == "interview" and self._cloud_session_id and self._agent is not None:
                save_messages(self._cloud_session_id, self._agent._messages)
            self.app.call_from_thread(self._set_chat_busy, False)

    def _set_chat_busy(self, busy: bool) -> None:
        inp = self.query_one("#chat-input", Input)
        inp.disabled = busy
        self.query_one("#btn-send", Button).disabled = busy
        if not busy:
            inp.focus()

    # ── Events ────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "btn-back":
            self.app.pop_screen()
        elif btn == "btn-stop":
            self._running = False
            self._on_agent_done()
        elif btn == "btn-send":
            self._submit_chat()
        elif btn == "btn-copy":
            self._copy_last_code()
        elif btn == "btn-reset":
            self._running = False
            self.query_one("#btn-reset", Button).disabled = True
            self._do_reset()

    def _copy_last_code(self) -> None:
        """Copy the last code block from the conversation to the clipboard."""
        if self._agent is None:
            return
        code = self._agent.last_code_block()
        if not code:
            self.notify("No code block found in this session.", severity="warning")
            return
        self.app.copy_to_clipboard(code)
        btn = self.query_one("#btn-copy", Button)
        btn.label = "✓ Copied!"
        btn.disabled = True
        self.set_timer(1.5, self._reset_copy_button)

    def _reset_copy_button(self) -> None:
        btn = self.query_one("#btn-copy", Button)
        btn.label = "⎘ Copy Code"
        btn.disabled = False

    @work(thread=True)
    def _do_reset(self) -> None:
        """Delete cloud messages then switch to a fresh session screen."""
        from ...cloud.db import reset_session
        ch = self._problem
        problem_slug = getattr(ch, "title_slug", None) or ch.title
        reset_session(problem_slug, self._mode)
        self.app.call_from_thread(
            self.app.switch_screen,
            AgentSessionScreen(ch, self._mode, self._user_code),
        )

    # ── Actions ───────────────────────────────────────────────────────

    def action_stop_agent(self) -> None:
        self._running = False
        self._on_agent_done()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_toggle_history(self) -> None:
        """Ctrl+H — toggle visibility of the prior session conversation."""
        self._history_visible = not self._history_visible
        panel = self.query_one("#prior-history", VerticalGroup)
        panel.display = self._history_visible
        if self._history_visible:
            self._scroll_to_bottom()

    def action_toggle_steps(self) -> None:
        """Ctrl+T — toggle visibility of background step content."""
        self._steps_visible = not self._steps_visible
        for block in self.query(BackgroundStep):
            block.toggle_content(self._steps_visible)

    def action_toggle_description(self) -> None:
        """Ctrl+D — toggle the problem description panel (interview mode only)."""
        if self._mode != "interview":
            return
        panel = self.query_one("#description-panel")
        panel.display = not panel.display
