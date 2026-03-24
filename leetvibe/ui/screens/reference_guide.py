"""ReferenceGuideScreen — Playbook mode: algorithm topics with notes and export."""

from __future__ import annotations

import json
import re
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Input, OptionList, RichLog, Static
from textual.widgets.option_list import Option

from ...data.topics import CATEGORIES, TIER_MAP, TOPICS
from ..theme import AMBER, DIM, EMBER, FIRE, GOLD, GREEN, LAVA, RED
from ..widgets.status_bar import StatusBar
from .base import BaseScreen

# ── Notes persistence ──────────────────────────────────────────────────────────

_NOTES_DIR  = Path.home() / ".leetvibe"
_NOTES_FILE = _NOTES_DIR / "notes.json"


def _load_notes() -> dict[str, str]:
    try:
        return json.loads(_NOTES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_notes(notes: dict[str, str]) -> None:
    try:
        _NOTES_DIR.mkdir(parents=True, exist_ok=True)
        _NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ── Rich markup helper ─────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escape [ so Rich doesn't interpret user content as markup tags."""
    return text.replace("[", r"\[")


# ── Difficulty badge helpers ───────────────────────────────────────────────────

_DIFF_COLOR = {"E": GREEN, "M": AMBER, "H": RED}
_DIFF_LABEL = {"E": "Easy", "M": "Med ", "H": "Hard"}


# ── Content renderer ───────────────────────────────────────────────────────────

def _sh(label: str) -> str:
    """Section header: accent bar + uppercase label."""
    return f"[{LAVA}]▍[/{LAVA}] [bold {FIRE}]{label.upper()}[/bold {FIRE}]"


def _render_title(title: str) -> str:
    """First word in FIRE, rest in default text."""
    words = title.split(" ", 1)
    if len(words) == 1:
        return f"[bold {FIRE}]{words[0]}[/bold {FIRE}]"
    return f"[bold {FIRE}]{words[0]}[/bold {FIRE}][bold] {words[1]}[/bold]"


def _pill_tags(recognize: str) -> str:
    """Extract double-quoted keywords from recognize text → amber pill tags."""
    tags = re.findall(r'"([^"]+)"', recognize)
    if not tags:
        return ""
    pills = [f"[on #1a1000][{AMBER}] {tag} [/{AMBER}][/on #1a1000]" for tag in tags]
    return "  " + " ".join(pills)


def _infobox(text: str) -> list[str]:
    """Render text in a softly dimmed infobox style."""
    return [f"  [{DIM}]{ln}[/{DIM}]" for ln in text.split("\n")]


def _code_block(block: str) -> list[str]:
    """Render a code block with box-drawing header and │-prefixed lines."""
    lines = [f"  [{DIM}]┌── python {'─' * 30}[/{DIM}]"]
    for ln in block.split("\n"):
        lines.append(f"  [{LAVA}]│[/{LAVA}] {ln}")
    lines.append(f"  [{DIM}]└{'─' * 41}[/{DIM}]")
    return lines


def _render_topic(topic: dict, note: str) -> str:
    """Build a Rich-markup string for the right panel."""

    # ── Pattern Selector (special layout) ───────────────────────────────
    if topic["slug"] == "_selector":
        lines: list[str] = [
            "",
            _render_title(topic["title"]),
            "",
            _sh("How to pick a pattern"),
            f"  [{DIM}]{'─' * 48}[/{DIM}]",
        ]
        for ln in _esc(topic["diagram"]).split("\n"):
            lines.append(f"  {ln}")
        lines += [
            f"  [{DIM}]{'─' * 48}[/{DIM}]",
            "",
            f"  [{DIM}]{_esc(topic['when'])}[/{DIM}]",
        ]
        return "\n".join(lines)

    title    = topic["title"]
    diagram  = _esc(topic.get("diagram", ""))
    when     = _esc(topic.get("when", ""))
    pattern  = _esc(topic.get("pattern", ""))
    pattern2 = _esc(topic.get("pattern2", ""))
    t_val    = _esc(topic.get("time", ""))
    s_val    = _esc(topic.get("space", ""))
    recognize = topic.get("recognize", "")   # parsed before escaping
    pitfalls  = _esc(topic.get("pitfalls", ""))
    related   = topic.get("related", [])

    lines: list[str] = [
        "",
        _render_title(title),
    ]

    # Keyword pill tags (extracted from quoted strings in recognize)
    tags_line = _pill_tags(recognize)
    if tags_line:
        lines.append(tags_line)
    lines.append("")

    # Recognise by
    if recognize:
        lines.append(_sh("Recognise by"))
        for ln in _esc(recognize).split("\n"):
            lines.append(f"  {ln}")
        lines.append("")

    # Diagram
    lines.append(_sh("Diagram"))
    lines += _infobox(diagram)
    lines.append("")

    # When to use
    lines.append(_sh("When to use"))
    lines += _infobox(when)
    lines.append("")

    # Pattern
    if pattern:
        lines.append(_sh("Pattern"))
        lines += _code_block(pattern)
        lines.append("")

    # Pattern variant
    if pattern2:
        lines.append(_sh("Pattern — Variant"))
        lines += _code_block(pattern2)
        lines.append("")

    # Complexity
    if t_val or s_val:
        lines.append(_sh("Complexity"))
        if t_val:
            lines.append(f"  Time   [{AMBER}]{t_val}[/{AMBER}]")
        if s_val:
            lines.append(f"  Space  [{AMBER}]{s_val}[/{AMBER}]")
        lines.append("")

    # Pitfalls
    if pitfalls:
        lines.append(_sh("Pitfalls"))
        for ln in pitfalls.split("\n"):
            lines.append(f"  [{RED}]{ln}[/{RED}]")
        lines.append("")

    # Classic Problems
    if topic.get("problems"):
        lines.append(_sh("Classic Problems"))
        for item in topic["problems"]:
            if isinstance(item, tuple):
                name, diff = item
                dc = _DIFF_COLOR.get(diff, DIM)
                dl = _DIFF_LABEL.get(diff, diff)
                lines.append(
                    f"  [{DIM}]•[/{DIM}] {_esc(name)}  [{dc}][{dl}][/{dc}]"
                )
            else:
                lines.append(f"  [{DIM}]•[/{DIM}] {_esc(str(item))}")
        lines.append("")

    # Related Topics
    if related:
        lines.append(_sh("Related Topics"))
        lines.append(
            "  " + "  ·  ".join(f"[{EMBER}]{r}[/{EMBER}]" for r in related)
        )
        lines.append("")

    # Notes
    if note.strip():
        lines.append(_sh("My Notes"))
        for note_line in note.strip().split("\n"):
            lines.append(f"  {_esc(note_line)}")
    else:
        lines.append(
            f"  [{DIM}]No notes yet — press [bold]N[/bold] to add one.[/{DIM}]"
        )

    return "\n".join(lines)


# ── Top breadcrumb bar ─────────────────────────────────────────────────────────

class PlaybookBreadcrumb(Horizontal):
    """Breadcrumb bar: Playbook › <topic>  with key hints on right."""

    def compose(self) -> ComposeResult:
        yield Static("", id="bc-left", markup=True)

    def set_topic(self, topic_title: str) -> None:
        text = (
            f"[bold {FIRE}]Playbook[/bold {FIRE}]  [{DIM}]›[/{DIM}]  "
        )
        if topic_title:
            text += f"{topic_title}"
        self.query_one("#bc-left", Static).update(text)


# ── Inline chat panel ──────────────────────────────────────────────────────────

class PlaybookChatPanel(Widget):
    """Inline AI chat panel — ask Vibe about the current topic."""

    def compose(self) -> ComposeResult:
        yield RichLog(id="chat-log", markup=True, wrap=True, highlight=False)
        yield Input(placeholder="Ask about this pattern…", id="chat-input")

    def set_topic(self, topic: dict) -> None:
        self._topic = topic

    def reset(self) -> None:
        self.query_one("#chat-log", RichLog).clear()

    def focus_input(self) -> None:
        self.query_one("#chat-input", Input).focus()

    def append_user(self, message: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[{DIM}]YOU[/{DIM}]")
        log.write(f"[on #1a1000][{AMBER}] {_esc(message)} [/{AMBER}][/on #1a1000]")
        log.write("")

    def append_ai_label(self) -> None:
        self.query_one("#chat-log", RichLog).write(f"[{DIM}]VIBE AI[/{DIM}]")

    def append_ai_line(self, line: str) -> None:
        self.query_one("#chat-log", RichLog).write(f"  {line}")

    def append_log(self, markup: str) -> None:
        """Legacy helper."""
        self.query_one("#chat-log", RichLog).write(markup)


# ── Filter helpers ─────────────────────────────────────────────────────────────

_TIER_LABEL = {1: "① Foundational", 2: "② Intermediate", 3: "③ Advanced"}
_CAT_NAMES  = [None] + [c["name"] for c in CATEGORIES]   # None = All
_TIER_CYCLE = [None, 1, 2, 3]                             # None = All


# ── Screen ─────────────────────────────────────────────────────────────────────

class ReferenceGuideScreen(BaseScreen):
    """Playbook mode — browse algorithm topics, add notes, and export to DOCX."""

    BINDINGS = [
        Binding("escape",  "pop_screen",      "← Back"),
        Binding("ctrl+q",  "quit_app",        "Quit"),
        Binding("c",       "cycle_category",  "Category",    show=False),
        Binding("t",       "cycle_tier",      "Tier",        show=False),
        Binding("e",       "explain_more",    "Explain More", show=False),
        Binding("p",       "practice",        "Practice",    show=False),
        Binding("n",       "edit_note",       "Edit Note",   show=False),
        Binding("x",       "export_docx",     "Export DOCX", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._current_idx: int = 0
        self._notes: dict[str, str] = {}
        self._chat_open: bool = False
        self._chat_history: list[dict] = []
        self._filter_cat: str | None = None   # None = All categories
        self._filter_tier: int | None = None  # None = All tiers

    # ── Filtered topic list ──────────────────────────────────────────────

    @property
    def _visible_topics(self) -> list[dict]:
        result = TOPICS
        if self._filter_cat is not None:
            result = [t for t in result if t.get("category") == self._filter_cat]
        if self._filter_tier is not None:
            result = [t for t in result if t.get("tier") == self._filter_tier]
        return result

    def compose(self) -> ComposeResult:
        yield PlaybookBreadcrumb(id="ref-breadcrumb")
        with Horizontal(id="ref-body"):
            with Vertical(id="ref-topics"):
                yield Static("", id="filter-bar", markup=True)
                yield OptionList(id="topic-list")
            with VerticalScroll(id="ref-content-scroll"):
                yield Static("", id="ref-content", markup=True)
            yield PlaybookChatPanel(id="chat-panel")

        yield StatusBar(
            hints=[
                ("↑↓",     "navigate",         None),
                ("C",      "category filter",  self.action_cycle_category),
                ("T",      "tier filter",      self.action_cycle_tier),
                ("E",      "ask Vibe AI",      self.action_explain_more),
                ("P",      "practice",         self.action_practice),
                ("N",      "edit note",        self.action_edit_note),
                ("X",      "export DOCX",      self.action_export_docx),
                ("Esc",    "go back",          self.action_pop_screen),
                ("Ctrl+Q", "quit",             self.action_quit_app),
            ],
            id="ref-status",
        )

    def on_mount(self) -> None:
        self._notes = _load_notes()
        self._rebuild_list()

    # ── Filter actions ───────────────────────────────────────────────────

    def action_cycle_category(self) -> None:
        idx = _CAT_NAMES.index(self._filter_cat)
        self._filter_cat = _CAT_NAMES[(idx + 1) % len(_CAT_NAMES)]
        self._rebuild_list()

    def action_cycle_tier(self) -> None:
        idx = _TIER_CYCLE.index(self._filter_tier)
        self._filter_tier = _TIER_CYCLE[(idx + 1) % len(_TIER_CYCLE)]
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        """Repopulate the OptionList from _visible_topics and reset selection."""
        visible = self._visible_topics
        topic_list = self.query_one("#topic-list", OptionList)
        topic_list.clear_options()
        for i, t in enumerate(visible):
            topic_list.add_option(Option(t["title"], id=f"topic-{i}"))
        self._current_idx = 0
        if visible:
            topic_list.highlighted = 0
        self._refresh_filter_bar()
        self._refresh_content()
        topic_list.focus()

    def _refresh_filter_bar(self) -> None:
        cat_label  = self._filter_cat or "All"
        tier_label = _TIER_LABEL.get(self._filter_tier, "All") if self._filter_tier else "All"
        count      = len(self._visible_topics)
        bar = (
            f"[{DIM}]Cat :[/{DIM}] [{AMBER}]{cat_label}[/{AMBER}]  "
            f"[{DIM}]Tier:[/{DIM}] [{AMBER}]{tier_label}[/{AMBER}]  "
            f"[{DIM}]({count} topics)[/{DIM}]"
        )
        self.query_one("#filter-bar", Static).update(bar)

    # ── Topic navigation ─────────────────────────────────────────────────

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self._current_idx = event.option_index
        self._refresh_content()
        if self._chat_open:
            visible = self._visible_topics
            if visible:
                panel = self.query_one(PlaybookChatPanel)
                panel.set_topic(visible[self._current_idx])
                panel.reset()
                self._chat_history = []

    def _refresh_content(self) -> None:
        visible = self._visible_topics
        if not visible:
            try:
                self.query_one("#ref-content", Static).update(
                    f"\n  [{DIM}]No topics match the current filters.[/{DIM}]"
                )
                self.query_one("#ref-breadcrumb", PlaybookBreadcrumb).set_topic("")
            except Exception:
                pass
            return
        topic = visible[self._current_idx]
        note  = self._notes.get(topic["slug"], "")
        try:
            self.query_one("#ref-content", Static).update(_render_topic(topic, note))
            self.query_one("#ref-content-scroll", VerticalScroll).scroll_home(animate=False)
            self.query_one("#ref-breadcrumb", PlaybookBreadcrumb).set_topic(topic["title"])
        except Exception:
            pass

    # ── Actions ──────────────────────────────────────────────────────────

    def action_explain_more(self) -> None:
        """Toggle the inline Vibe AI chat panel for the current topic."""
        panel = self.query_one(PlaybookChatPanel)
        if self._chat_open:
            panel.remove_class("open")
            self._chat_open = False
            self.query_one("#topic-list", OptionList).focus()
        else:
            visible = self._visible_topics
            if not visible:
                return
            topic = visible[self._current_idx]
            panel.set_topic(topic)
            panel.reset()
            self._chat_history = []
            panel.add_class("open")
            self._chat_open = True
            panel.focus_input()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "chat-input":
            return
        message = event.value.strip()
        if not message:
            return
        event.input.clear()
        panel = self.query_one(PlaybookChatPanel)
        panel.append_user(message)
        self._stream_vibe_response(message)

    @work(thread=True)
    def _stream_vibe_response(self, user_message: str) -> None:
        panel   = self.query_one(PlaybookChatPanel)
        visible = self._visible_topics
        if not visible:
            return
        topic = visible[self._current_idx]

        system_prompt = (
            f"You are Vibe, an expert algorithm tutor inside LeetVibe. "
            f"The user is studying the '{topic['title']}' pattern. "
            f"Answer clearly and concisely. Use short code snippets when helpful. "
            f"Keep responses focused on this algorithm pattern."
        )

        self._chat_history.append({"role": "user", "content": user_message})

        try:
            from mistralai import Mistral
            from ...config import load_config

            config = load_config()
            client = Mistral(api_key=config.mistral_api_key)

            self.app.call_from_thread(panel.append_ai_label)

            full_response = ""
            buffer = ""

            with client.chat.stream(
                model=getattr(config, "model", "mistral-large-latest") or "mistral-large-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self._chat_history,
                ],
            ) as stream:
                for event in stream:
                    try:
                        chunk = event.data.choices[0].delta.content or ""
                    except (AttributeError, IndexError):
                        continue
                    if chunk:
                        full_response += chunk
                        buffer += chunk
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            self.app.call_from_thread(
                                panel.append_ai_line, _esc(line)
                            )

            if buffer:
                self.app.call_from_thread(panel.append_ai_line, _esc(buffer))

            self.app.call_from_thread(panel.append_log, "")
            self._chat_history.append({"role": "assistant", "content": full_response})

        except Exception as exc:
            self.app.call_from_thread(
                panel.append_log,
                f"  [{RED}]Error: {_esc(str(exc)[:120])}[/{RED}]",
            )

    def action_practice(self) -> None:
        """Open problem list pre-filtered to the current topic."""
        visible = self._visible_topics
        if not visible:
            return
        from .problem_list import ProblemListScreen
        topic = visible[self._current_idx]
        self.app.push_screen(ProblemListScreen(mode="learn", initial_topic=topic["slug"]))

    def action_edit_note(self) -> None:
        """Open the notes modal for the current topic."""
        visible = self._visible_topics
        if not visible:
            return
        from .notes_modal import NotesModal
        topic    = visible[self._current_idx]
        existing = self._notes.get(topic["slug"], "")

        def _on_result(result: str | None) -> None:
            if result is not None:
                self._notes[topic["slug"]] = result
                _save_notes(self._notes)
                self._refresh_content()
                self.notify(
                    f"Note saved for {topic['title']}",
                    severity="information",
                )

        self.app.push_screen(NotesModal(topic["title"], existing), _on_result)

    def action_export_docx(self) -> None:
        """Export all topics and notes to a DOCX file in a background thread."""
        self.notify("Exporting…", severity="information")
        self._run_export()

    @work(thread=True)
    def _run_export(self) -> None:
        try:
            from ...docx_exporter import export_reference_docx
            path = export_reference_docx(TOPICS, self._notes)
            self.app.call_from_thread(
                self.notify,
                f"Saved → {path}",
                severity="information",
                timeout=8,
            )
        except ImportError:
            self.app.call_from_thread(
                self.notify,
                "python-docx not installed — run: pip install python-docx",
                severity="error",
            )
        except Exception as exc:
            self.app.call_from_thread(
                self.notify,
                f"Export failed: {str(exc).replace('[', '(').replace(']', ')')}",
                severity="error",
            )
