"""AgentSessionScreen — bubble-chat layout for AI sessions.

While the workflow runs, nothing streams into the transcript: a shimmer
indicator names the step currently executing. When the run completes, the
full answer prints as ONE fire-bordered "leetvibe" bubble with every step under
its own header, followed by the mnemonic card. Follow-up Q&A and interview
turns use the same bubble idiom.
"""

from __future__ import annotations

import re
import threading

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.widgets import Button, Input, Static

from leetvibe.problem_loader import Problem
from leetvibe.ui.keys import reinsert_swallowed_space
from leetvibe.ui.markup import MARKUP_RE, render_agent_markup
from leetvibe.ui.theme import FIRE, GREEN, RED
from leetvibe.ui.widgets import (
    ChatBubbleLog,
    ProblemCard,
    StatusBar,
    StepAnswerBubble,
    ThinkingIndicator,
)
from leetvibe.ui.screens.base import BaseScreen

# Strip markdown bold (**text**) and heading (### text) markers before matching
_MD_DECORATION_RE = re.compile(r"^[*#\s]+|[*#\s]+$")
# Matches "STEP N — Title", "STEP N - Title", "STEP N: Title" (case-insensitive)
# Works whether or not the line is wrapped in **…** or ### …
_STEP_RE = re.compile(r"^\s*STEP\s+(\d+)\s*[—–\-:]+\s*(.*)", re.IGNORECASE)
# Matches standalone "Call toolname(...)" lines emitted by the LLM before tool dispatch
_TOOL_CALL_LINE_RE = re.compile(r"^Call\s+\w+\s*\(.*\)\s*$", re.IGNORECASE)
# Matches the machine-parsed "Pattern: <slug>" line the model appends after its
# synthesis paragraph (see SYSTEM_PROMPT/PAIR_PROMPT STEP 7) — never shown to the
# user. Tolerant of the model wrapping "Pattern"/the slug in extra markdown
# (**bold**, `backticks`, a leading bullet, trailing punctuation) despite being
# told to write it exactly as "Pattern: <slug>" — any of that previously made
# the strict format miss the line entirely, leaking it into the visible
# transcript (live) or silently breaking mnemonic extraction (the .search()
# use below), since models don't always follow formatting instructions to the
# letter. Shared verbatim by both use sites so a decoration case fixed for one
# is automatically fixed for the other.
_PATTERN_LINE_RE = re.compile(
    r"^[-•\s]*\**pattern\**\s*:?\s*\**\s*`?([\w-]+)`?\**\s*\.?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


class AgentSessionScreen(BaseScreen):
    """Full-screen AI session with buffered steps and bubble follow-up chat."""

    BINDINGS = [
        Binding("escape",  "pop_screen",          "← Back"),
        Binding("ctrl+s",  "stop_agent",          "■ Stop",        show=False),
        Binding("ctrl+r",  "show_history",        "Prior Session", show=False),
        Binding("ctrl+d",  "toggle_description",  "Problem",       show=False, priority=True),
        Binding("ctrl+g",  "toggle_hints",        "Hints",         show=False, priority=True),
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
        # Streaming buffers — nothing is written to the transcript mid-run
        self._step_mode = False
        self._step_buffers: list[dict] = []   # {"num": int, "title": str, "lines": [str]}
        self._chat_lines: list[str] = []      # non-step content (interview / follow-ups)
        self._in_fence = False                # inside a ``` block — no step detection
        self._stopped = False                 # user pressed Stop mid-run
        self._chat_stopped = False            # user pressed Stop mid-follow-up
        self._session_done = False   # guard against double _on_agent_done
        self._cloud_session_id: str | None = None  # set once by _run_agent
        self._prior_messages: list[dict] = []      # saved messages from last session
        self._history_printed = False              # Ctrl+R prints prior chat once

    # ── Layout ────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        ch = self._problem
        diff_color = {"easy": GREEN, "medium": "#FFB300", "hard": RED}.get(
            ch.difficulty.lower(), "#888888"
        )

        mode_label = {"learn": "Learn", "pair": "Pair", "interview": "Interview"}.get(
            self._mode, self._mode.title()
        )
        with Horizontal(id="session-bar"):
            with Horizontal(id="session-bar-left"):
                yield Button("← Back", id="btn-back")
            yield Static(
                f"[{diff_color}]{ch.title}[/{diff_color}]"
                f"  [dim]·[/dim]  [bold {FIRE}]{mode_label}[/bold {FIRE}]",
                id="session-title",
            )
            with Horizontal(id="session-bar-right"):
                yield Button("⎘ Copy Code", id="btn-copy", disabled=True)
                yield Button("↺ Reset", id="btn-reset")

        with Horizontal(id="session-body"):
            with VerticalScroll(id="description-panel"):
                yield ProblemCard(ch)
            with Vertical(id="chat-column"):
                yield Static(
                    "📎  Resumed from last session — press Ctrl+R to view prior conversation.",
                    id="resume-hint",
                )
                yield VerticalScroll(id="chat-scroll")
                yield ThinkingIndicator(id="session-thinking")

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
                ("Ctrl+D", "toggle problem description",      self.action_toggle_description),  # 0 — interview only
                ("Ctrl+S", "stop agent",      self.action_stop_agent),           # 1
                ("Ctrl+R", "review prior session", self.action_show_history),    # 2 — hidden until history exists
                ("Esc",    "go back",         self.action_pop_screen),           # 3
                ("Ctrl+Q", "quit",            self.action_quit_app),             # 4
            ],
            show_count=False,
            id="session-status",
        )

    # ── Widget accessors ──────────────────────────────────────────────

    def _scroll(self) -> VerticalScroll:
        return self.query_one("#chat-scroll", VerticalScroll)

    def _log(self) -> ChatBubbleLog:
        """Return the trailing ChatBubbleLog segment in #chat-scroll, creating
        one if the transcript is empty or the last segment is a
        StepAnswerBubble (a live mounted widget, not a log — the next plain
        bubble needs its own fresh log to write into)."""
        scroll = self._scroll()
        children = scroll.children
        if children and isinstance(children[-1], ChatBubbleLog):
            return children[-1]  # type: ignore[return-value]
        log = ChatBubbleLog(
            renderer=render_agent_markup,
            markup=True, wrap=True, highlight=False, min_width=1,
            classes="bubble-log",
        )
        scroll.mount(log)
        return log

    def _scroll_to_end(self) -> None:
        self._scroll().scroll_end(animate=False)

    def _indicator(self) -> ThinkingIndicator:
        return self.query_one("#session-thinking", ThinkingIndicator)

    def _speaker(self) -> str:
        return "alex" if self._mode == "interview" else "leetvibe"

    def _equalize_bar_columns(self) -> None:
        """Make #session-bar-left/-right the same width — whichever is
        naturally wider — so #session-title (1fr) is always centered on the
        actual screen, using the maximum width available given whichever
        buttons this mode actually shows (e.g. Copy Code + Reset hidden in
        interview mode) instead of a fixed reservation on both sides."""
        left = self.query_one("#session-bar-left")
        right = self.query_one("#session-bar-right")
        width = max(left.region.width, right.region.width)
        left.styles.width = width
        right.styles.width = width

    # ── Lifecycle ─────────────────────────────────────────────────────

    def on_mount(self) -> None:
        status = self.query_one("#session-status", StatusBar)
        # Ctrl+R (index 2) is hidden until prior history is confirmed
        status.set_hint_visible(2, False)
        # Ctrl+D (problem description) is available in every mode now — Learn/
        # Pair just start with the panel closed (see action_toggle_description).
        status.set_hint_visible(0, True)
        # Esc/Ctrl+Q are already learned from Home/ProblemList/ProblemWorkspace
        # (every screen that leads here) — no need to repeat them.
        status.set_hint_visible(3, False)
        status.set_hint_visible(4, False)
        if self._mode == "interview":
            # No opening label — Alex's greeting is the first thing the user should see
            # Problem description starts open so the user can read along;
            # Ctrl+D still toggles it.
            self.query_one("#description-panel").display = True
            try:
                self.query_one("#btn-copy", Button).display = False
                self.query_one("#btn-reset", Button).display = False
            except Exception:
                pass
        # Runs after this mount's layout (and the display=False above) has
        # settled, so the columns' auto widths reflect what's actually shown.
        self.call_after_refresh(self._equalize_bar_columns)
        # The thinking indicator is NOT shown yet — only once the agent actually
        # starts generating (resumed sessions never stream, so never show it).
        # Input and Send are already disabled from compose().
        self._running = True
        # Interview mode has no numbered steps — buffer as one conversational turn
        self._step_mode = self._mode != "interview"
        self._run_agent(self._problem, self._mode, self._user_code)

    def on_unmount(self) -> None:
        """Stop any in-progress audio when the screen is closed."""
        try:
            from leetvibe.ai.skills.voice_narrator.server import stop_playback
            stop_playback()
        except Exception:
            pass

    # ── Worker ────────────────────────────────────────────────────────

    @work(thread=True)
    def _run_agent(self, problem: Problem, mode: str, user_code: str) -> None:
        """Background thread: streams agent output into step buffers."""
        from leetvibe.cloud.db import (
            load_messages,
            reset_session,
            save_messages,
            upsert_session,
        )
        from leetvibe.ai.agent import PAIR_PROMPT_VERSION, SYSTEM_PROMPT_VERSION
        from leetvibe.problem_loader import session_slug

        problem_slug = session_slug(problem)

        try:
            from leetvibe.config import load_config
            config = load_config()

            # Interview history is never resumed (always starts fresh below),
            # so compatibility doesn't apply — None skips the staleness check
            # entirely instead of wiping transcripts nothing reads back.
            current_version = (
                None if mode == "interview"
                else PAIR_PROMPT_VERSION if mode == "pair" and user_code.strip()
                else SYSTEM_PROMPT_VERSION
            )

            self._cloud_session_id, stale = upsert_session(
                problem_slug, problem.difficulty, mode, current_version
            )
            if self._cloud_session_id is None:
                # Not signed in (or the account was signed out mid-session) —
                # every cloud call degrades silently, so say so explicitly
                # instead of leaving the user to discover it never resumes.
                self.app.call_from_thread(self._warn_not_signed_in)
            elif stale:
                # Saved under an older prompt contract — resuming it would
                # feed the model history it no longer understands and render
                # step formats the UI no longer knows about. Wipe it (not a
                # user-initiated reset) and start clean instead of resuming.
                reset_session(problem_slug, mode, manual=False)

            if mode == "interview":
                from leetvibe.ai.agent import InterviewAgent
                self._agent = InterviewAgent(config)
                self.app.call_from_thread(self._set_chat_busy, True)
                for chunk in self._agent.start_streaming(problem):
                    if not self._running:
                        break
                    self.app.call_from_thread(self._buffer_chunk, chunk)
                self.app.call_from_thread(self._flush_buffer)
            else:
                from leetvibe.ai.agent import VibeAgent, PAIR_PROMPT, SYSTEM_PROMPT
                self._agent = VibeAgent(config)
                if mode == "pair" and not user_code.strip():
                    # Pair with an empty editor silently falls back to the
                    # Learn workflow — tell the user instead of pretending.
                    self.app.call_from_thread(
                        self._note,
                        "[dim]No code found in the editor — running the full "
                        "Learn walkthrough instead.[/dim]",
                    )
                prior_messages = (
                    load_messages(problem_slug, mode)
                    if self._cloud_session_id and not stale
                    else []
                )
                if prior_messages:
                    system = (
                        PAIR_PROMPT if mode == "pair" and user_code.strip()
                        else SYSTEM_PROMPT
                    )
                    self._agent.inject_history(
                        [{"role": "system", "content": system}, *prior_messages],
                        problem=problem,
                    )
                    self._prior_messages = prior_messages
                    self.app.call_from_thread(self._enable_history_hint)
                    self.app.call_from_thread(self._show_resume_hint)
                else:
                    self.app.call_from_thread(self._set_chat_busy, True)
                    for chunk in self._agent.solve_streaming(problem, mode, user_code):
                        if not self._running:
                            break
                        self.app.call_from_thread(self._buffer_chunk, chunk)
                    self.app.call_from_thread(self._flush_buffer)

        except Exception as exc:
            safe = str(exc).replace("\n", " ")
            self.app.call_from_thread(self._show_error, f"Fatal error: {safe}")
        finally:
            # Finish the UI first — the cloud save is slow network I/O and must
            # not keep the thinking indicator visible after content is printed.
            self.app.call_from_thread(self._on_agent_done)
            if self._cloud_session_id and self._agent is not None:
                save_messages(self._cloud_session_id, self._agent._messages)

    # ── Thread-safe UI helpers ────────────────────────────────────────

    def _note(self, line: str) -> None:
        self._log().append_raw(line)
        self._scroll_to_end()

    def _show_resume_hint(self) -> None:
        self.query_one("#resume-hint", Static).display = True

    def _show_error(self, message: str) -> None:
        self._log().append_error(message)
        self._scroll_to_end()

    def _warn_not_signed_in(self) -> None:
        self.notify(
            "This session will not be saved — sign in to sync your progress.",
            title="Not signed in",
            severity="warning",
            timeout=8,
        )

    def _enable_history_hint(self) -> None:
        if self._mode != "interview":
            self.query_one("#session-status", StatusBar).set_hint_visible(2, True)

    def _buffer_chunk(self, chunk: str) -> None:
        """Accumulate streaming chunks; route complete lines to buffers."""
        self._line_buffer += chunk
        while "\n" in self._line_buffer:
            line, self._line_buffer = self._line_buffer.split("\n", 1)
            self._write_line(line)

    def _flush_buffer(self) -> None:
        if self._line_buffer:
            self._write_line(self._line_buffer)
            self._line_buffer = ""

    def _write_line(self, line: str) -> None:
        """Route one streamed line into the step/chat buffers (no UI writes)."""
        if not self._step_mode:
            self._chat_lines.append(line)
            return

        clean = MARKUP_RE.sub("", line).strip()
        # Track code fences: "# Step 1: …" comments inside code must not be
        # mistaken for workflow steps. Fence lines stay in the buffer.
        if clean.startswith("```"):
            self._in_fence = not self._in_fence
            self._append_step_line(line)
            return
        if not self._in_fence:
            # Strip markdown bold/heading decorators before matching
            decorated = _MD_DECORATION_RE.sub("", clean).strip()
            m = _STEP_RE.match(decorated)
            if m:
                num, title = int(m.group(1)), m.group(2).strip()
                # Steps must move forward: smaller/equal numbers are prose
                # ("**Step 1: …**" sub-headings). Accepting any increase — not
                # just last+1 — keeps one swallowed header (e.g. lost inside a
                # derailed tool call) from cascading over the rest of the run.
                last = self._step_buffers[-1]["num"] if self._step_buffers else 0
                if num > last:
                    # A run_code/analyze_complexity call the model makes before
                    # any step header (the opening "Run Your Code" tool call
                    # always lands here) buffers into _chat_lines below, since
                    # no step exists yet to hold it. Fold that preamble into
                    # the step it actually belongs to instead of letting
                    # _post_answer_bubble flush it as its own detached bubble.
                    carried = list(self._chat_lines) if not self._step_buffers else []
                    self._chat_lines = []
                    self._step_buffers.append(
                        {"num": num, "title": title, "lines": carried}
                    )
                    self._indicator().set_label(f"step {num} — {title.lower()}…")
                    return
            # Suppress bare "Call toolname()" annotations — the summary line covers it
            if _TOOL_CALL_LINE_RE.match(decorated):
                return
            # Suppress the trailing "Pattern: <slug>" line — parsed separately, never shown
            if _PATTERN_LINE_RE.match(decorated):
                return
        self._append_step_line(line)

    def _append_step_line(self, line: str) -> None:
        if self._step_buffers:
            self._step_buffers[-1]["lines"].append(line)
        else:
            self._chat_lines.append(line)

    # ── Bubble posting ────────────────────────────────────────────────

    def _flush_chat_bubble(self) -> None:
        """Post buffered non-step content as one AI bubble."""
        content = "\n".join(self._chat_lines).strip()
        self._chat_lines = []
        if content:
            self._log().append_ai(content, speaker=self._speaker())
            self._scroll_to_end()

    def _post_answer_bubble(self) -> None:
        """Print the full answer — every step as its own collapsible section
        inside one titled bubble (all expanded initially; the user collapses
        them manually), mounted directly rather than written to a log."""
        # Content that arrived before any step marker (retries, preambles)
        self._flush_chat_bubble()
        steps = [
            {
                "num": step["num"],
                "title": step["title"].title(),
                "content": "\n".join(step["lines"]).strip(),
            }
            for step in self._step_buffers
            if "\n".join(step["lines"]).strip()
        ]
        if steps:
            bubble = StepAnswerBubble(self._speaker(), steps, renderer=render_agent_markup)
            self._scroll().mount(bubble)
            self._scroll_to_end()
        if self._stopped:
            self._log().append_raw("[dim]■ session stopped[/dim]")
            self._scroll_to_end()

    def _on_agent_done(self) -> None:
        if self._session_done:
            return
        self._session_done = True
        self._running = False
        self._step_mode = False

        if self._mode == "interview":
            lines = list(self._chat_lines)
            self._flush_chat_bubble()
            # Narrate the AI's initial greeting (the problem intro + question)
            threading.Thread(
                target=self._narrate_interview_turn,
                args=(lines,),
                daemon=True,
            ).start()
        else:
            # Capture synthesis text before posting (buffers stay intact)
            synthesis_text = ""
            if self._step_buffers:
                synthesis_text = self._extract_narration_text(
                    self._step_buffers[-1]["lines"]
                )
            self._post_answer_bubble()
            pattern = self._extract_algorithm_pattern(self._agent) if self._agent else ""
            log_data = self._extract_log_session_data(self._agent) if self._agent else {}
            self._session_summary = {
                "title": self._problem.title,
                "difficulty": self._problem.difficulty,
                "topics": self._problem.topics or [],
                "algorithm_pattern": pattern,
                "synthesis": synthesis_text,
                "complexity": log_data.get("final_complexity", ""),
            }
            # Only after an actual run — a resumed session posts no answer
            # bubble, so a floating mnemonic card would be noise.
            if self._step_buffers:
                self._trigger_mnemonic()

        self.query_one("#btn-copy", Button).disabled = False
        inp = self.query_one("#chat-input", Input)
        inp.placeholder = "Ask a follow-up question…"
        self._set_chat_busy(False)

    # ── Synthesis text extraction ─────────────────────────────────────

    @staticmethod
    def _extract_narration_text(lines: list[str]) -> str:
        """Clean final-step lines into plain prose suitable for TTS / summaries."""
        # Patterns to skip: tool-call summary/detail/table and spinner lines
        _SKIP_RE = re.compile(r"^\s*[⚙→▶◈✎■│┌├└]|Calling \w+|⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏")
        _BACKTICK_RE = re.compile(r"`[^`]*`")

        clean_lines = []
        for line in lines:
            plain = MARKUP_RE.sub("", line).strip()
            if not plain or _SKIP_RE.search(plain):
                continue
            plain = _BACKTICK_RE.sub("", plain).strip()
            if plain:
                clean_lines.append(plain)

        return " ".join(clean_lines).strip()

    # ── Post-session mnemonic ─────────────────────────────────────────

    def _trigger_mnemonic(self) -> None:
        """Generate and append the algorithm mnemonic after the session."""
        if self._agent is None:
            return
        threading.Thread(
            target=self._post_session_worker,
            args=(self, self._agent),
            daemon=True,
        ).start()

    @staticmethod
    def _post_session_worker(screen: "AgentSessionScreen", agent: object) -> None:
        """Fetch the mnemonic and append it as a card below the final bubble."""
        try:
            pattern = AgentSessionScreen._extract_algorithm_pattern(agent)
            if not pattern:
                # Model skipped the "Pattern:" line — fall back to the
                # problem's first topic so the mnemonic doesn't silently vanish
                topics = getattr(screen._problem, "topics", None) or []
                pattern = topics[0] if topics else ""
            if not pattern:
                return
            mnemonic = AgentSessionScreen._get_or_generate_mnemonic(pattern)
            if mnemonic:
                screen.app.call_from_thread(screen._append_mnemonic, mnemonic)
        except Exception:
            pass

    def _append_mnemonic(self, text: str) -> None:
        self._log().append_mnemonic(text)
        self._scroll_to_end()

    @staticmethod
    def _extract_algorithm_pattern(agent: object) -> str:
        """Find the algorithm pattern from the model's trailing "Pattern: <slug>" line."""
        for msg in getattr(agent, "_messages", []):
            if msg.get("role") == "assistant":
                m = _PATTERN_LINE_RE.search(msg.get("content") or "")
                if m:
                    return m.group(1)
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
            from leetvibe.config import load_config
            resp = Mistral(api_key=load_config().mistral_api_key).chat.complete(
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
                        tc_val = data.get("time") or data.get("time_complexity") or ""
                        sc_val = data.get("space") or data.get("space_complexity") or ""
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
        """Flush buffers, post the reply bubble, then queue narration."""
        self._flush_buffer()
        lines = list(self._chat_lines)
        self._flush_chat_bubble()
        threading.Thread(
            target=self._narrate_interview_turn,
            args=(lines,),
            daemon=True,
        ).start()

    @staticmethod
    def _narrate_interview_turn(lines: list[str]) -> None:
        """Extract the AI response text and narrate with the coach voice preset."""
        text = AgentSessionScreen._extract_interview_snippet(lines)
        if not text:
            return
        try:
            from leetvibe.ai.skills.voice_narrator.server import narrate
            narrate(text, voice_type="coach")
        except Exception:
            pass

    @staticmethod
    def _extract_interview_snippet(lines: list[str]) -> str:
        """Return the full AI interview response, clean of markup."""
        clean = []
        for line in lines:
            plain = MARKUP_RE.sub("", line).strip()
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

    def _add_user_bubble(self, text: str) -> None:
        self._log().append_user(text)
        self._scroll_to_end()

    def _finish_chat_turn(self) -> None:
        self._flush_buffer()
        self._flush_chat_bubble()

    @work(thread=True)
    def _run_chat(self, user_message: str) -> None:
        from leetvibe.cloud.db import save_messages

        self._chat_running = True
        self._chat_stopped = False
        self.app.call_from_thread(self._set_chat_busy, True)
        self.app.call_from_thread(self._add_user_bubble, user_message)
        full_content = ""
        try:
            if self._mode == "interview":
                agent = self._agent
            else:
                if self._concept_agent is None:
                    from leetvibe.ai.agent import ConceptAgent
                    from leetvibe.config import load_config
                    self._concept_agent = ConceptAgent(load_config(), self._session_summary)
                agent = self._concept_agent

            if agent is not None:
                for chunk in agent.chat_streaming(user_message):
                    if self._chat_stopped:
                        break
                    full_content += chunk
                    self.app.call_from_thread(self._buffer_chunk, chunk)
            if self._mode == "interview":
                self.app.call_from_thread(self._flush_and_narrate_interview)
            else:
                self.app.call_from_thread(self._finish_chat_turn)
            if self._chat_stopped:
                self.app.call_from_thread(self._note, "[dim]■ stopped[/dim]")
        except Exception as exc:
            safe = str(exc).replace("\n", " ")
            self.app.call_from_thread(self._show_error, f"Error: {safe}")
        finally:
            self._chat_running = False
            # Hide the indicator before the cloud save — the reply bubble is
            # already printed (and, in interview mode, being narrated).
            self.app.call_from_thread(self._set_chat_busy, False)
            if self._cloud_session_id and self._agent is not None:
                if self._mode == "interview":
                    save_messages(self._cloud_session_id, self._agent._messages)
                else:
                    # Learn/Pair follow-ups run through the lightweight
                    # ConceptAgent (its own message list, seeded with just the
                    # session summary) so they never touch self._agent._messages
                    # — the list save_messages/load_messages actually persists
                    # and replays. Mirror the exchange into it so a follow-up
                    # question survives a relaunch instead of silently vanishing.
                    self._agent._messages.append(
                        {"role": "user", "content": user_message}
                    )
                    if full_content:
                        self._agent._messages.append(
                            {"role": "assistant", "content": full_content}
                        )
                    save_messages(self._cloud_session_id, self._agent._messages)

    def _set_chat_busy(self, busy: bool) -> None:
        inp = self.query_one("#chat-input", Input)
        inp.disabled = busy
        # While the agent generates, the Send slot doubles as a Stop control
        send = self.query_one("#btn-send", Button)
        send.disabled = False
        if busy:
            send.label = "Stop"
            send.add_class("-stop")
        else:
            send.label = "Send"
            send.remove_class("-stop")
        indicator = self._indicator()
        if busy:
            indicator.set_label("thinking…")
        indicator.display = busy
        if not busy:
            inp.focus()

    # ── Events ────────────────────────────────────────────────────────

    def on_key(self, event: Key) -> None:
        reinsert_swallowed_space(event, self.query_one("#chat-input", Input))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "btn-back":
            self.app.pop_screen()
        elif btn == "btn-send":
            if self._chat_running or self._running:
                self._stop_current()
            else:
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
        from leetvibe.cloud.db import reset_session
        from leetvibe.problem_loader import session_slug
        ch = self._problem
        problem_slug = session_slug(ch)
        reset_session(problem_slug, self._mode)
        self.app.call_from_thread(
            self.app.switch_screen,
            AgentSessionScreen(ch, self._mode, self._user_code),
        )

    # ── Actions ───────────────────────────────────────────────────────

    def action_stop_agent(self) -> None:
        self._stop_current()

    def _stop_current(self) -> None:
        """Stop whichever generation is in flight — initial run or follow-up turn."""
        if self._chat_running:
            self._chat_stopped = True
        elif self._running:
            self._stopped = True
            self._running = False
            self._on_agent_done()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_show_history(self) -> None:
        """Ctrl+R — reconstruct the prior session through the same
        step-parsing/consolidation pipeline a live run uses (_write_line +
        _post_answer_bubble), instead of one bubble per raw stored message.

        The raw replay used to show every intermediate tool-calling turn as
        its own bubble (live sessions hide those seams behind one final
        bubble), and silently dropped tool-result blocks entirely — they're
        only ever yielded live (format_tool_block), never persisted, so
        this regenerates them from the saved (possibly compacted) tool
        JSON instead of skipping role == "tool" outright.
        """
        if not self._prior_messages or self._history_printed:
            return
        self._history_printed = True
        # _on_agent_done() (called once the resume's inject_history returns,
        # since no live streaming happens on that path) already reset this to
        # False — force it back on so the replayed "Step N: …" markers below
        # are parsed into _step_buffers instead of dumped into one flat bubble.
        self._step_mode = True
        from leetvibe.ai.agent import format_tool_block

        for i, msg in enumerate(self._prior_messages):
            role = msg.get("role", "")
            if i == 0 and role == "user":
                # The auto-generated problem-context prompt that kicks off
                # every session (agent.py's solve_streaming/_build_prompt) —
                # never shown live either, so it shouldn't appear as a "you"
                # bubble here.
                continue
            if role == "user":
                self._flush_replayed_bubble()
                content = str(msg.get("content") or "").strip()
                if content:
                    self._log().append_user(content)
                    self._scroll_to_end()
            elif role == "assistant":
                for line in str(msg.get("content") or "").split("\n"):
                    self._write_line(line)
            elif role == "tool":
                block = format_tool_block(
                    msg.get("name", ""), str(msg.get("content") or "")
                )
                for line in block.split("\n"):
                    self._write_line(line)
        self._flush_replayed_bubble()
        self.query_one("#resume-hint", Static).display = False
        self.query_one("#session-status", StatusBar).set_hint_visible(2, False)

    def _flush_replayed_bubble(self) -> None:
        """Post whatever step/chat buffers action_show_history has
        accumulated so far as one consolidated bubble (matching
        _post_answer_bubble's live format), then reset them so a later
        live follow-up question starts from a clean buffer."""
        if self._step_buffers or self._chat_lines:
            self._post_answer_bubble()
        self._step_buffers = []
        self._chat_lines = []
        self._in_fence = False

    def action_toggle_description(self) -> None:
        """Ctrl+D — toggle the problem description panel. Available in every
        mode: Interview starts it open (nothing else is on screen to refer
        back to), Learn/Pair start it hidden (drafted in ProblemWorkspaceScreen
        and there to glance back at, not read fresh)."""
        panel = self.query_one("#description-panel")
        panel.display = not panel.display

    def action_toggle_hints(self) -> None:
        """Ctrl+G — toggle hints inside the problem description panel."""
        if self._mode != "interview":
            return
        card = self.query_one(ProblemCard)
        card.show_hints = not card.show_hints
