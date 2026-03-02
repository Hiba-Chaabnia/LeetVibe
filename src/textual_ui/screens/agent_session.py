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

from ...challenge_loader import Challenge
from ..theme import FIRE, GREEN, RED
from ..widgets.challenge_card import ChallengeCard
from ..widgets.status_bar import StatusBar
from .base import BaseScreen

# Strip Rich markup tags like [bold], [/dim], [#FF0000] before regex matching
_MARKUP_RE = re.compile(r"\[/?[^\]]*\]")
# Strip markdown bold (**text**) and heading (### text) markers before matching
_MD_DECORATION_RE = re.compile(r"^[*#\s]+|[*#\s]+$")
# Matches "STEP N — Title", "STEP N - Title", "STEP N: Title" (case-insensitive)
# Works whether or not the line is wrapped in **…** or ### …
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
            icon = f"[bold {GREEN}]✓[/bold {GREEN}]"
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
            f"[bold {FIRE}]━━  Step 7 — {self._title}  ━━[/bold {FIRE}]",
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


class NarrationPanel(Static):
    """Post-session on-demand voice playback panel."""

    DEFAULT_CSS = """
    NarrationPanel {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    NarrationPanel .narr-header {
        width: 100%;
        height: 1;
        padding: 0 1;
        color: #555555;
    }
    NarrationPanel .narr-row {
        width: 100%;
        height: 3;
        padding: 0 1;
        align: left middle;
    }
    NarrationPanel Button {
        background: transparent;
        border: round #444444;
        color: #888888;
        height: 3;
        min-width: 0;
        padding: 0 2;
    }
    NarrationPanel Button:hover {
        border: round #FF8205;
        color: #FF8205;
    }
    NarrationPanel Button:disabled {
        color: #444444;
        border: round #333333;
    }
    NarrationPanel #narr-stop {
        color: #E53935;
        border: round #E53935;
    }
    NarrationPanel #narr-stop:disabled {
        color: #444444;
        border: round #333333;
    }
    """

    def __init__(self, items: list[tuple[str, str, str]]) -> None:
        # items: list of (label, text_to_speak, voice_type)
        super().__init__()
        self._items = items
        self._active_btn: Button | None = None
        self._active_label: str = ""

    def compose(self) -> ComposeResult:
        yield Static(
            "[dim]━━  🔊 Voice Playback  ━━[/dim]",
            markup=True,
            classes="narr-header",
        )
        for i, (label, _text, _voice) in enumerate(self._items):
            with Horizontal(classes="narr-row"):
                yield Button(f"▶  {label}", id=f"narr-btn-{i}")
        with Horizontal(classes="narr-row"):
            yield Button("■  Stop", id="narr-stop", disabled=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""

        if btn_id == "narr-stop":
            try:
                from skills.voice_narrator.server import stop_playback
                stop_playback()
            except Exception:
                pass
            return

        if not btn_id.startswith("narr-btn-"):
            return
        idx = int(btn_id.split("-")[-1])
        if idx >= len(self._items):
            return
        label, text, voice_type = self._items[idx]
        btn = event.button
        btn.label = "⠋  Playing…"
        btn.disabled = True
        self._active_btn = btn
        self._active_label = label
        try:
            self.query_one("#narr-stop", Button).disabled = False
        except Exception:
            pass

        def _play_and_restore() -> None:
            try:
                from skills.voice_narrator.server import narrate_blocking
                narrate_blocking(text, voice_type=voice_type)
            except Exception:
                pass
            self.app.call_from_thread(self._restore_btn, btn, label)

        threading.Thread(target=_play_and_restore, daemon=True).start()

    def _restore_btn(self, btn: Button, label: str) -> None:
        btn.label = f"✓  {label}"
        btn.disabled = False
        self._active_btn = None
        try:
            self.query_one("#narr-stop", Button).disabled = True
        except Exception:
            pass


class MnemonicBlock(Static):
    """Displays the algorithm pattern mnemonic after session completion."""

    DEFAULT_CSS = """
    MnemonicBlock {
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
    }
    MnemonicBlock .mnemonic-header {
        width: 100%;
        height: 1;
        padding: 0 1;
    }
    MnemonicBlock .mnemonic-text {
        width: 100%;
        height: auto;
        padding: 1 2;
        color: #FFD700;
        text-style: italic;
        border-left: heavy #FFD700;
    }
    """

    def __init__(self, mnemonic: str, pattern: str) -> None:
        super().__init__()
        self._mnemonic = mnemonic
        self._pattern = pattern

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold #FFD700]━━  💡 {self._pattern}  ━━[/bold #FFD700]",
            markup=True,
            classes="mnemonic-header",
        )
        yield Static(
            self._mnemonic,
            markup=False,
            classes="mnemonic-text",
        )


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


class AgentSessionScreen(BaseScreen):
    """Full-screen AI session with step-aware rendering and follow-up chat."""

    BINDINGS = [
        Binding("escape",  "pop_screen",          "← Back"),
        Binding("ctrl+s",  "stop_agent",          "■ Stop",        show=False),
        Binding("ctrl+h",  "toggle_history",      "Prior Session", show=False),
        Binding("ctrl+t",  "toggle_steps",        "Toggle Steps",  show=False),
        Binding("ctrl+d",  "toggle_description",  "Problem",       show=False, priority=True),
    ]

    DEFAULT_CSS = f"""
    AgentSessionScreen {{
        background: #121212;
    }}

    /* ── Top bar ─────────────────────────────────────────────────── */
    #session-bar {{
        height: 5;
        background: #1a1a1a;
        border-bottom: solid {FIRE};
        padding: 0 1;
        align: left middle;
    }}
    #session-title {{
        width: 1fr;
        height: 3;
        content-align: center middle;
        color: {FIRE};
        text-style: bold;
    }}
    #session-bar Button {{
        background: transparent;
        padding: 0 1;
        min-width: 0;
        height: 3;
    }}
    #session-bar Button:focus,
    #session-bar Button.-active {{
        background: transparent;
    }}
    #btn-back        {{ color: #aaaaaa; border: round #444444; text-style: dim; }}
    #btn-stop        {{ color: {RED};   border: round {RED}; }}
    #btn-copy        {{ color: {GREEN}; border: round {GREEN}; }}
    #btn-copy:disabled   {{ color: #333333; border: round #333333; }}
    #btn-reset       {{ color: #888888; border: round #444444; text-style: dim; }}
    #btn-reset:disabled  {{ color: #333333; border: round #333333; }}

    /* ── Prior history panel ─────────────────────────────────── */
    #prior-history {{
        width: 100%;
        height: auto;
        background: #0e0e0e;
        border-bottom: solid #333333;
        padding: 0 1 1 1;
        display: none;
    }}
    #prior-history-title {{
        color: #555555;
        text-style: italic;
        padding: 0 1;
        margin-bottom: 1;
    }}

    /* ── Body: description panel + chat side by side ─────────────── */
    #session-body {{
        height: 1fr;
        width: 100%;
    }}
    #description-panel {{
        width: 45%;
        height: 100%;
        background: #0d0d0d;
        border-right: solid #333333;
        padding: 0 1 1 1;
        display: none;
    }}

    /* ── Chat scroll (fills remaining space) ─────────────────────── */
    ChatScroll {{
        height: 100%;
        width: 1fr;
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
    #chat-input {{
        width: 1fr;
        background: #121212;
        color: #e0e0e0;
        border: round #444444;
    }}
    #chat-input:focus {{
        background: #121212;
        border: round {FIRE};
    }}
    #chat-input:disabled {{ color: #555555; border: round #2a2a2a; }}
    #btn-send {{
        width: auto;
        height: 3;
        border: round {FIRE};
        background: transparent;
        color: {FIRE};
        padding: 0 2;
        min-width: 6;
        content-align: center middle;
    }}
    #btn-send:focus, #btn-send.-active {{ background: transparent; }}
    #btn-send:disabled {{ color: #444444; border: round #444444; }}
    #session-status    {{ background: #121212; }}
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
        self._prior_messages: list[dict] = []      # saved messages from last session
        self._history_visible = False              # Ctrl+O toggle state

    # ── Layout ────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        ch = self._challenge
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
                yield ChallengeCard(ch)
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
            ],
            show_count=False,
            id="session-status",
        )

    # ── Lifecycle ─────────────────────────────────────────────────────

    def on_mount(self) -> None:
        ch = self._challenge
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
            from ...vibe_agent import VibeAgent, COACH_PROMPT, SYSTEM_PROMPT, INTERVIEW_PROMPT

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

            if prior_messages and mode != "interview":
                # Resume: inject saved history so follow-ups have full context.
                # Skip the full solve workflow — the AI already ran it last time.
                # Interview mode always starts fresh — no resuming.
                if mode == "interview":
                    system = INTERVIEW_PROMPT
                    self._agent._interview_mode = True
                elif mode == "coach" and user_code.strip():
                    system = COACH_PROMPT
                else:
                    system = SYSTEM_PROMPT
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
        else:
            # Extract step 7 text now while _current_final is still in scope
            step7_text = ""
            if self._current_final is not None:
                step7_text = self._extract_narration_text(self._current_final._lines)
            self._trigger_post_session_audio(step7_text)

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
        # Strip Rich markup tags like [bold #abc], [/dim], etc.
        _MARKUP_RE = re.compile(r"\[/?[^\]]*\]")
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

    # ── Post-session audio (mnemonic + voice panel) ──────────────────

    def _mount_mnemonic_block(self, mnemonic: str, pattern: str) -> None:
        """Mount the mnemonic widget into the messages area."""
        block = MnemonicBlock(mnemonic, pattern)
        self.query_one("#messages", VerticalGroup).mount(block)
        self._scroll_to_bottom()

    def _mount_narration_panel(self, items: list[tuple[str, str, str]]) -> None:
        """Mount the on-demand voice playback panel."""
        panel = NarrationPanel(items)
        self.query_one("#messages", VerticalGroup).mount(panel)
        self._scroll_to_bottom()

    def _trigger_post_session_audio(self, step7_text: str = "") -> None:
        """Launch the post-session worker to build the voice playback panel."""
        if self._agent is None:
            return
        threading.Thread(
            target=self._post_session_worker,
            args=(self, self._challenge, self._agent, step7_text),
            daemon=True,
        ).start()

    @staticmethod
    def _post_session_worker(
        screen: "AgentSessionScreen",
        challenge: object,
        agent: object,
        step7_text: str,
    ) -> None:
        """Generate mnemonic + recap texts and mount the voice playback panel."""
        try:
            has_voice = bool(os.environ.get("ELEVENLABS_API_KEY"))
            items: list[tuple[str, str, str]] = []

            # ── Step 7 explanation ────────────────────────────────────
            if step7_text:
                items.append(("Step 7 Explanation", step7_text, "mentor"))

            # ── Mnemonic ──────────────────────────────────────────────
            pattern = AgentSessionScreen._extract_algorithm_pattern(agent)
            if pattern:
                mnemonic = AgentSessionScreen._get_or_generate_mnemonic(pattern)
                if mnemonic:
                    screen.app.call_from_thread(
                        screen._mount_mnemonic_block, mnemonic, pattern
                    )
                    items.append((f"Algorithm Mnemonic: {pattern}", mnemonic, "mentor"))

            # ── Recap ─────────────────────────────────────────────────
            log_data = AgentSessionScreen._extract_log_session_data(agent)
            recap = AgentSessionScreen._generate_recap_text(challenge, log_data)
            if recap:
                items.append(("Session Recap", recap, "mentor"))

            # ── Mount playback panel ───────────────────────────────────
            if has_voice and items:
                screen.app.call_from_thread(screen._mount_narration_panel, items)

        except Exception as exc:
            screen.app.call_from_thread(
                screen.notify, f"Post-session error: {exc}",
                severity="error", timeout=4,
            )

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
            return resp.choices[0].message.content.strip().strip("\"'")
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

    @staticmethod
    def _generate_recap_text(challenge: object, log_data: dict) -> str:
        """Call Mistral to write a 2-sentence podcast recap; template on failure."""
        title = log_data.get("problem_title") or getattr(challenge, "title", "the problem")
        difficulty = (log_data.get("difficulty") or getattr(challenge, "difficulty", "")).capitalize()
        time_s = int(log_data.get("time_seconds") or 0)
        complexity = log_data.get("final_complexity", "")
        solved = log_data.get("solved", True)
        approaches = int(log_data.get("approaches_tried") or 1)

        context = (
            f"Problem: {title}. Difficulty: {difficulty}. "
            f"Solved: {solved}. Time: {time_s}s. "
            f"Final complexity: {complexity}. Attempts: {approaches}."
        )

        try:
            from mistralai import Mistral
            client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY", ""))
            resp = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a calm technical mentor summarizing a coding session. "
                            "Write exactly 2 clear sentences: what was solved and the key algorithmic insight. "
                            "Be precise and direct. No exclamation marks, no hype, no emojis, no markdown."
                        ),
                    },
                    {"role": "user", "content": context},
                ],
                max_tokens=80,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return AgentSessionScreen._template_recap(title, difficulty, time_s, complexity, solved, approaches)

    @staticmethod
    def _template_recap(
        title: str, difficulty: str, time_s: int, complexity: str, solved: bool, approaches: int
    ) -> str:
        time_str = f"{time_s // 60}m {time_s % 60}s" if time_s >= 60 else f"{time_s}s"
        outcome = "Solved" if solved else "Worked through"
        first = f"{outcome} {title} — {difficulty} — in {time_str}."
        second = f"Final complexity: {complexity}." if complexity else (
            "First attempt, clean run." if approaches == 1 else f"{approaches} attempts to nail it."
        )
        return f"{first} {second}"

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
            from skills.voice_narrator.server import narrate
            narrate(text, voice_type="coach")
        except Exception:
            pass

    @staticmethod
    def _extract_interview_snippet(lines: list[str]) -> str:
        """Return the full AI interview response, clean of markup."""
        _MARKUP_RE = re.compile(r"\[/?[^\]]*\]")
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
            for chunk in self._agent.chat_streaming(user_message):
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
        ch = self._challenge
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
