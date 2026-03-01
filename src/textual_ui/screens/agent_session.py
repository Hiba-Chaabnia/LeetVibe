"""AgentSessionScreen — mistral-vibe style chat layout for AI sessions."""

from __future__ import annotations

import re

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalGroup, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from ...challenge_loader import Challenge
from ..widgets.status_bar import StatusBar

_FIRE = "#FF8205"
_GREEN = "#00C44F"
_BLUE = "#4A9EFF"
_RED = "#E53935"

# Strip Rich markup tags like [bold], [/dim], [#FF0000] before regex matching
_MARKUP_RE = re.compile(r"\[/?[^\]]*\]")
# Matches "STEP N — Title", "STEP N - Title", "STEP N: Title" (case-insensitive)
_STEP_RE = re.compile(r"^\s*STEP\s+(\d+)\s*[—–\-:]+\s*(.*)", re.IGNORECASE)

# ── Chat widgets ───────────────────────────────────────────────────────────────


class ChatScroll(VerticalScroll):
    """Performance-optimised scroll container — skips cascading style recalcs."""

    def update_node_styles(self, animate: bool = True) -> None:  # noqa: FBT001
        pass


class UserMessage(Static):
    """User / problem turn: orange heavy left-border bubble."""

    DEFAULT_CSS = """
    UserMessage {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    UserMessage .msg-content {
        height: auto;
        padding: 0 1;
        border-left: heavy #FF8205;
        color: #FF8205;
        text-style: bold;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def compose(self) -> ComposeResult:
        yield Static(self._text, markup=True, classes="msg-content")


class BackgroundStep(Static):
    """Steps 1-6 and 8+: dim spinner header + collapsible content (hidden by default)."""

    SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    DEFAULT_CSS = """
    BackgroundStep {
        width: 100%;
        height: auto;
    }
    BackgroundStep .step-header {
        width: 100%;
        height: 1;
        padding: 0 1;
    }
    BackgroundStep .step-content {
        width: 100%;
        height: auto;
        padding: 0 0 0 4;
        color: #505050;
    }
    """

    def __init__(self, step_num: int, title: str, content_visible: bool = False) -> None:
        super().__init__()
        self._step_num = step_num
        self._title = title
        self._spinner_idx = 0
        self._done = False
        self._content_visible = content_visible
        self._lines: list[str] = []
        self._header_widget: Static | None = None
        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        self._header_widget = Static(self._render_header(), markup=True, classes="step-header")
        yield self._header_widget
        self._content_widget = Static("", markup=True, classes="step-content")
        yield self._content_widget

    def on_mount(self) -> None:
        # Apply initial visibility after the widget is fully in the DOM
        if self._content_widget is not None:
            self._content_widget.display = self._content_visible

    def _render_header(self) -> str:
        if self._done:
            icon = f"[bold {_GREEN}]✓[/bold {_GREEN}]"
        else:
            icon = f"[dim]{self.SPINNER[self._spinner_idx % len(self.SPINNER)]}[/dim]"
        return f"{icon} [dim]Step {self._step_num} — {self._title}[/dim]"

    def advance_spinner(self) -> None:
        if not self._done:
            self._spinner_idx += 1
            if self._header_widget is not None:
                try:
                    self._header_widget.update(self._render_header())
                except Exception:
                    pass

    def mark_done(self) -> None:
        self._done = True
        if self._header_widget is not None:
            try:
                self._header_widget.update(self._render_header())
            except Exception:
                pass

    def write_line(self, line: str) -> None:
        self._lines.append(line)
        if self._content_widget is not None:
            try:
                self._content_widget.update("\n".join(self._lines))
            except Exception:
                pass

    def toggle_content(self, visible: bool) -> None:
        self._content_visible = visible
        if self._content_widget is not None:
            self._content_widget.display = visible


class FinalAnswer(Static):
    """Step 7: bold white answer block — always fully visible."""

    DEFAULT_CSS = """
    FinalAnswer {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    FinalAnswer .final-sep {
        width: 100%;
        height: 1;
        padding: 0 1;
    }
    FinalAnswer .final-content {
        width: 100%;
        height: auto;
        padding: 0 1;
        color: #ffffff;
        text-style: bold;
    }
    """

    def __init__(self, title: str) -> None:
        super().__init__()
        self._title = title
        self._lines: list[str] = []
        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {_FIRE}]━━  Step 7 — {self._title}  ━━[/bold {_FIRE}]",
            markup=True,
            classes="final-sep",
        )
        self._content_widget = Static("", markup=True, classes="final-content")
        yield self._content_widget

    def write_line(self, line: str) -> None:
        self._lines.append(line)
        if self._content_widget is not None:
            try:
                self._content_widget.update("\n".join(self._lines))
            except Exception:
                pass


class AssistantBlock(Static):
    """One follow-up AI turn (or fallback block): accumulates streamed Rich-markup lines."""

    DEFAULT_CSS = """
    AssistantBlock {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    AssistantBlock Static {
        width: 100%;
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._lines: list[str] = []
        self._display: Static | None = None

    def compose(self) -> ComposeResult:
        self._display = Static("", markup=True)
        yield self._display

    def write_line(self, line: str) -> None:
        self._lines.append(line)
        if self._display is not None:
            try:
                self._display.update("\n".join(self._lines))
            except Exception:
                pass


# ── Screen ─────────────────────────────────────────────────────────────────────


class AgentSessionScreen(Screen):
    """Full-screen AI session with step-aware rendering and follow-up chat."""

    BINDINGS = [
        Binding("escape", "pop_screen", "← Back"),
        Binding("s", "stop_agent", "■ Stop", show=False),
        Binding("ctrl+o", "toggle_steps", "Toggle Steps", show=False),
    ]

    DEFAULT_CSS = f"""
    AgentSessionScreen {{
        background: #121212;
    }}

    /* ── Top bar ─────────────────────────────────────────────────── */
    #session-bar {{
        height: 3;
        background: #1a1a1a;
        border-bottom: solid {_FIRE};
        padding: 0 1;
        align: left middle;
    }}
    #session-title {{
        width: 1fr;
        content-align: center middle;
        color: {_FIRE};
        text-style: bold;
    }}
    #session-bar Button {{
        border: none;
        background: transparent;
        padding: 0 1;
        min-width: 0;
        height: 1;
        color: #aaaaaa;
    }}
    #btn-back:hover {{ background: #2a2a2a; color: #e0e0e0; }}
    #btn-stop        {{ color: {_RED}; }}
    #btn-stop:hover  {{ background: #2a0000; }}
    #btn-copy        {{ color: {_GREEN}; }}
    #btn-copy:hover  {{ background: #0a2a0a; }}
    #btn-copy:disabled {{ color: #333333; }}

    /* ── Chat scroll (fills remaining space) ─────────────────────── */
    ChatScroll {{
        height: 1fr;
        width: 100%;
        background: transparent;
    }}
    #messages {{
        width: 100%;
        height: auto;
        padding: 0 1 1 1;
    }}

    /* ── Input container (always visible) ───────────────────────── */
    #chat-input-container {{
        height: auto;
        width: 100%;
        padding: 0 1 1 1;
    }}
    #input-box {{
        height: auto;
        width: 100%;
        background: transparent;
    }}
    #prompt {{
        width: auto;
        color: {_FIRE};
        text-style: bold;
        padding: 0 1;
        content-align: left middle;
    }}
    /* Let Input keep its natural height: 3 so the content row never collapses. */
    #chat-input {{
        width: 1fr;
        background: #121212;
        color: #e0e0e0;
        border: tall #444444;
    }}
    #chat-input:focus {{
        background: #121212;
        border: tall {_FIRE};
    }}
    #chat-input:disabled {{ color: #555555; border: tall #2a2a2a; }}
    #btn-send {{
        width: auto;
        border: none;
        background: transparent;
        color: {_FIRE};
        padding: 0 2;
        min-width: 0;
        content-align: center middle;
    }}
    #btn-send:hover    {{ background: #3a2200; }}
    #btn-send:disabled {{ color: #444444; }}
    """

    def __init__(
        self,
        challenge: Challenge,
        mode: str = "learn",
        user_code: str = "",
    ) -> None:
        super().__init__()
        self._challenge = challenge
        self._mode = mode
        self._user_code = user_code
        self._running = False
        self._line_buffer = ""
        self._agent = None
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

    # ── Layout ────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        ch = self._challenge
        diff_color = {"easy": _GREEN, "medium": "#FFB300", "hard": _RED}.get(
            ch.difficulty.lower(), "#888888"
        )

        with Horizontal(id="session-bar"):
            yield Button("← Back", id="btn-back")
            yield Static(
                f"LeetVibe AI  ●  [{diff_color}]{ch.title}[/{diff_color}]"
                f"  [dim]({ch.difficulty})[/dim]",
                id="session-title",
            )
            yield Button("⎘ Copy Code", id="btn-copy", disabled=True)
            yield Button("■ Stop", id="btn-stop")

        with ChatScroll(id="chat-scroll"):
            yield VerticalGroup(id="messages")

        with Vertical(id="chat-input-container"):
            with Horizontal(id="input-box"):
                yield Static("›", id="prompt")
                yield Input(
                    placeholder="Session in progress…",
                    id="chat-input",
                    disabled=True,
                )
                yield Button("Send", id="btn-send", disabled=True)

        yield StatusBar(
            hints=[
                ("Esc",    "Back",         self.action_pop_screen),
                ("S",      "Stop",         self.action_stop_agent),
                ("Ctrl+O", "Toggle Steps", self.action_toggle_steps),
            ],
            show_count=False,
            id="session-status",
        )

    # ── Lifecycle ─────────────────────────────────────────────────────

    def on_mount(self) -> None:
        ch = self._challenge
        diff_color = {"easy": _GREEN, "medium": "#FFB300", "hard": _RED}.get(
            ch.difficulty.lower(), "#888888"
        )
        label = (
            f"[dim]Mode: {self._mode.title()}[/dim]  ·  "
            f"[{diff_color}]{ch.title}[/{diff_color}]  "
            f"[dim]({ch.difficulty})[/dim]"
        )
        self._mount_user_message(label)
        self._spinner_timer = self.set_interval(0.1, self._tick_spinner)
        self._running = True
        self._step_mode = True
        self._run_agent(self._challenge, self._mode, self._user_code)

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

        if step_num == 7:
            self._is_final = True
            final = FinalAnswer(title)
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
    def _run_agent(self, challenge: Challenge, mode: str, user_code: str) -> None:
        """Background thread: streams agent output into step widgets."""
        from ...session_log import SessionLog
        from ...cloud.db import load_messages, save_messages, upsert_session

        session_log = SessionLog(challenge, mode, user_code)
        error_msg: str | None = None

        problem_slug = getattr(challenge, "title_slug", None) or challenge.title

        try:
            from ...config import load_config
            from ...vibe_agent import VibeAgent, COACH_PROMPT, SYSTEM_PROMPT

            self._agent = VibeAgent(load_config())

            # Establish (or retrieve) the cloud session row
            self._cloud_session_id = upsert_session(
                problem_slug, challenge.difficulty, mode
            )

            # Check for a prior conversation to resume
            prior_messages = (
                load_messages(problem_slug, mode)
                if self._cloud_session_id
                else []
            )

            if prior_messages:
                # Resume: inject saved history so follow-ups have full context.
                # Skip the full solve workflow — the AI already ran it last time.
                system = (
                    COACH_PROMPT
                    if (mode == "coach" and user_code.strip())
                    else SYSTEM_PROMPT
                )
                self._agent.inject_history(
                    [{"role": "system", "content": system}, *prior_messages]
                )
                self.app.call_from_thread(
                    self._write_line,
                    "[dim]📎  Resumed from last session — "
                    "ask a follow-up question below.[/dim]",
                )
            else:
                # Fresh session: run the full solve workflow
                for chunk in self._agent.solve_streaming(challenge, mode, user_code):
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
            # Strip Rich markup before regex matching
            clean = _MARKUP_RE.sub("", line).strip()
            m = _STEP_RE.match(clean)
            if m:
                self._start_new_step(int(m.group(1)), m.group(2).strip())
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
            # Follow-up chat: plain AssistantBlock
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

        # Append session-complete separator
        if self._current_final is not None:
            self._current_final.write_line("")
            self._current_final.write_line(f"[bold {_FIRE}]━━  Session complete  ━━[/bold {_FIRE}]")
        elif self._current_block is not None:
            self._current_block.write_line("")
            self._current_block.write_line(f"[bold {_FIRE}]━━  Session complete  ━━[/bold {_FIRE}]")

        self.query_one("#btn-stop", Button).disabled = True
        self.query_one("#btn-copy", Button).disabled = False
        inp = self.query_one("#chat-input", Input)
        inp.placeholder = "Ask a follow-up question…"
        self._set_chat_busy(False)

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
            for chunk in self._agent.chat_streaming(user_message):
                self.app.call_from_thread(self._buffer_chunk, chunk)
            self.app.call_from_thread(self._flush_buffer)
        except Exception as exc:
            safe = str(exc).replace("[", r"\[").replace("\n", " ")
            self.app.call_from_thread(
                self._write_line, f"[bold red]Error: {safe}[/bold red]"
            )
        finally:
            self._chat_running = False
            if self._cloud_session_id and self._agent is not None:
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

    # ── Actions ───────────────────────────────────────────────────────

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_stop_agent(self) -> None:
        self._running = False
        self._on_agent_done()

    def action_toggle_steps(self) -> None:
        """Ctrl+O — toggle visibility of background step content."""
        self._steps_visible = not self._steps_visible
        for block in self.query(BackgroundStep):
            block.toggle_content(self._steps_visible)
