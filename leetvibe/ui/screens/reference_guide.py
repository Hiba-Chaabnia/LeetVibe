"""ReferenceGuideScreen — Playbook mode: algorithm topics with notes and export."""

from __future__ import annotations

import json
import re
from pathlib import Path

from rich.panel import Panel
from rich.text import Text

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual.widgets import Button, Input, OptionList, RichLog, Select, Static, TextArea
from textual.widgets.option_list import Option

from ...data.topics import CATEGORIES, TIER_MAP, TOPICS
from ..theme import AMBER, DIM, EMBER, FIRE, GOLD, GRADIENT, GREEN, LAVA, RED, SHIMMER
from ..widgets.status_bar import StatusBar
from ..widgets.truncated_select import TruncatedSelect
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


_HISTORIES_FILE = _NOTES_DIR / "chat_histories.json"


def _load_histories() -> dict[str, list[dict]]:
    try:
        return json.loads(_HISTORIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_histories(histories: dict[str, list[dict]]) -> None:
    try:
        _NOTES_DIR.mkdir(parents=True, exist_ok=True)
        _HISTORIES_FILE.write_text(
            json.dumps(histories, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


# ── Database topic slug cache ──────────────────────────────────────────────────

_DB_TOPIC_SLUGS: set[str] | None = None


def _get_db_topic_slugs() -> set[str]:
    """Return the set of topic tags that exist in the problems database (cached)."""
    global _DB_TOPIC_SLUGS
    if _DB_TOPIC_SLUGS is None:
        from ...problem_loader import load_all_problems
        problems = load_all_problems()
        _DB_TOPIC_SLUGS = {t for ch in problems for t in (ch.topics or [])}
    return _DB_TOPIC_SLUGS


# ── Rich markup helper ─────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escape [ so Rich doesn't interpret user content as markup tags."""
    return text.replace("[", r"\[")


_SPINNER_FRAMES: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


# ── Difficulty badge helpers ───────────────────────────────────────────────────

_DIFF_COLOR = {"E": GREEN, "M": AMBER, "H": RED}
_DIFF_LABEL = {"E": "Easy", "M": "Med ", "H": "Hard"}


# ── Content renderer ───────────────────────────────────────────────────────────

def _sh(label: str, idx: int = 0) -> str:
    """Section header: title-case label in a cycling gradient color."""
    color = GRADIENT[idx % len(GRADIENT)]
    return f"[bold {color}]{label.title()}[/bold {color}]"


def _render_title(title: str) -> str:
    """Title with fire gradient per character."""
    title = title.upper()
    n = len(title)
    chars = []
    for i, ch in enumerate(title):
        idx = min(int(i / max(n - 1, 1) * (len(GRADIENT) - 1) + 0.5), len(GRADIENT) - 1)
        color = GRADIENT[idx]
        chars.append(f"[bold {color}]{ch}[/bold {color}]")
    return "".join(chars)




def _infobox(text: str) -> list[str]:
    """Render text in a softly dimmed infobox style."""
    return [f"  [{DIM}]{ln}[/{DIM}]" for ln in text.split("\n")]


def _code_block(block: str, width: int = 24) -> list[str]:
    """Render a code block with box-drawing header and │-prefixed lines."""
    # "  ┌── python " = 13 chars; fill rest with dashes up to total width
    dash_header = max(2, width - 13)
    dash_footer = max(2, width - 3)
    lines = [f"  [{DIM}]┌── python {'─' * dash_header}[/{DIM}]"]
    for ln in block.split("\n"):
        lines.append(f"  [{DIM}]│[/{DIM}] {ln}")
    lines.append(f"  [{DIM}]└{'─' * dash_footer}[/{DIM}]")
    return lines


def _md_inline(line: str) -> str:
    """Convert inline markdown to Rich markup, safely escaping literal brackets."""
    line = line.replace("[", "\x00")
    line = re.sub(r"\*\*(.+?)\*\*", r"[bold]\1[/bold]", line)
    line = re.sub(r"`([^`]+)`", rf"[bold {AMBER}]\1[/bold {AMBER}]", line)
    if re.match(r"^[-•]\s", line):
        line = f"  [{DIM}]•[/{DIM}] " + line[2:]
    line = line.replace("\x00", r"\[")
    return line


def _render_response_to_markup(content: str) -> str:
    """Convert AI response markdown to a Rich markup string for Panel display."""
    lines_out: list[str] = []
    in_code = False
    code_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("```"):
            if in_code:
                for rendered in _code_block("\n".join(code_lines), width=22):
                    lines_out.append(rendered)
                lines_out.append("")
                code_lines = []
                in_code = False
            else:
                in_code = True
        elif in_code:
            code_lines.append(line)
        elif line.strip():
            lines_out.append(_md_inline(line))
        else:
            lines_out.append("")

    if in_code and code_lines:
        for rendered in _code_block("\n".join(code_lines), width=22):
            lines_out.append(rendered)

    while lines_out and not lines_out[-1].strip():
        lines_out.pop()

    return "\n".join(lines_out)


def _build_topic_context(topic: dict) -> str:
    """Build a concise reference string for the AI system prompt."""
    parts = [f"Pattern: {topic['title']}"]
    if topic.get("recognize"):
        parts.append(f"Recognised by: {topic['recognize']}")
    if topic.get("intuition"):
        parts.append(f"Intuition: {topic['intuition']}")
    if topic.get("time") or topic.get("space"):
        parts.append(
            f"Complexity: Time {topic.get('time', '?')}, Space {topic.get('space', '?')}"
        )
    if topic.get("patterns"):
        parts.append("Code patterns:")
        for pat in topic["patterns"]:
            parts.append(f"  {pat['name']}:")
            parts.append(f"```python\n{pat['code']}\n```")
    if topic.get("variants"):
        parts.append(f"Variants: {topic['variants']}")
    if topic.get("pitfalls"):
        parts.append(f"Pitfalls: {topic['pitfalls']}")
    return "\n".join(parts)


def _render_topic(topic: dict, note: str) -> str:
    """Build a Rich-markup string for the right panel."""

    # ── Pattern Selector (special layout) ───────────────────────────────
    if topic["slug"] == "_selector":
        lines: list[str] = [
            "",
            _sh("How to pick a pattern", 0),
            f"  [{DIM}]{'─' * 48}[/{DIM}]",
        ]
        for ln in _esc(topic["diagram"]).split("\n"):
            lines.append(f"  {ln}")
        lines += [
            f"  [{DIM}]{'─' * 48}[/{DIM}]",
            "",
            f"  [{DIM}]{_esc(topic.get('when', ''))}[/{DIM}]",
        ]
        return "\n".join(lines)

    diagram   = _esc(topic.get("diagram", ""))
    t_val     = _esc(topic.get("time", ""))
    s_val     = _esc(topic.get("space", ""))
    recognize = _esc(topic.get("recognize", ""))
    intuition = _esc(topic.get("intuition", ""))
    pitfalls  = _esc(topic.get("pitfalls", ""))
    variants  = _esc(topic.get("variants", ""))
    confusion = _esc(topic.get("confusion", ""))
    follow_up = _esc(topic.get("follow_up_questions", ""))
    related   = topic.get("related", [])

    lines: list[str] = [""]
    h = 0  # gradient index for section headers

    # Recognised by
    if recognize:
        lines.append(_sh("Recognised by", h)); h += 1
        for ln in recognize.split("\n"):
            lines.append(f"  [{DIM}]{ln}[/{DIM}]")
        lines.append("")

    # Intuition
    if intuition:
        lines.append(_sh("Intuition", h)); h += 1
        for ln in intuition.split("\n"):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Diagram
    lines.append(_sh("Diagram", h)); h += 1
    lines += _infobox(diagram)
    lines.append("")

    # Patterns
    patterns = topic.get("patterns", [])
    if patterns:
        lines.append(_sh("Patterns", h)); h += 1
        for i, pat in enumerate(patterns, 1):
            lines.append(f"  [bold #ffffff]{i}. {_esc(pat['name'])}[/bold #ffffff]")
            lines += _code_block(_esc(pat["code"]), width=48)
            lines.append("")

    # Variants
    if variants:
        lines.append(_sh("Variants", h)); h += 1
        for ln in variants.split("\n"):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Complexity
    if t_val or s_val:
        lines.append(_sh("Complexity", h)); h += 1
        if t_val:
            lines.append(f"  Time   [{AMBER}]{t_val}[/{AMBER}]")
        if s_val:
            lines.append(f"  Space  [{AMBER}]{s_val}[/{AMBER}]")
        lines.append("")

    # Pitfalls
    if pitfalls:
        lines.append(_sh("Pitfalls", h)); h += 1
        for ln in pitfalls.split("\n"):
            lines.append(f"  [{RED}]{ln}[/{RED}]")
        lines.append("")

    # Don't mix up with
    if confusion:
        lines.append(_sh("Don't mix up with", h)); h += 1
        for ln in confusion.split("\n"):
            lines.append(f"  [{DIM}]{ln}[/{DIM}]")
        lines.append("")

    # Follow-up questions
    if follow_up:
        lines.append(_sh("Follow-up questions", h)); h += 1
        for ln in follow_up.split("\n"):
            lines.append(f"  [{GOLD}]{ln}[/{GOLD}]")
        lines.append("")

    # Classic Problems
    if topic.get("problems"):
        lines.append(_sh("Classic Problems", h)); h += 1
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
        lines.append(_sh("Related Topics", h)); h += 1
        lines.append(
            "  " + "  ·  ".join(f"[{EMBER}]{r}[/{EMBER}]" for r in related)
        )
        lines.append("")

    # Notes
    if note.strip():
        lines.append(_sh("My Notes", h))
        for note_line in note.strip().split("\n"):
            lines.append(f"  {_esc(note_line)}")
    else:
        lines.append(
            f"  [{DIM}]No notes yet — press [bold]N[/bold] to add one.[/{DIM}]"
        )

    return "\n".join(lines)


# ── Inline chat panel ──────────────────────────────────────────────────────────

class ThinkingIndicator(Static):
    """Animated spinner + shimmering 'thinking…' label."""

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._offset: int = 0
        self._frame: int = 0

    def on_mount(self) -> None:
        self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        if not self.display:
            return
        self._offset = (self._offset + 1) % len(SHIMMER)
        self._frame = (self._frame + 1) % len(_SPINNER_FRAMES)
        self.update(self._build_text())

    def _build_text(self) -> Text:
        text = Text()
        text.append("  ")
        text.append(_SPINNER_FRAMES[self._frame], style=f"bold {FIRE}")
        text.append(" ")
        for i, ch in enumerate("thinking…"):
            color = SHIMMER[(i + self._offset) % len(SHIMMER)]
            text.append(ch, style=f"bold {color}")
        return text


class PlaybookChatPanel(Widget):
    """Inline AI chat panel — ask Vibe about the current topic."""

    class Cleared(Message):
        """Posted when the user presses the reset button."""

    class Toggled(Message):
        """Posted when the panel is expanded or collapsed."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="chat-header"):
            expand_btn = Button("◀", id="chat-expand", classes="chat-expand-btn")
            expand_btn.tooltip = "Expand chat panel"
            expand_btn.can_focus = False
            yield expand_btn
            yield Static("", id="chat-header-spacer")
            reset_btn = Button("🗑", id="chat-reset", classes="chat-reset-btn")
            reset_btn.tooltip = "Clear chat history"
            reset_btn.can_focus = False
            yield reset_btn
        chat_log = RichLog(id="chat-log", markup=True, wrap=True, highlight=False, min_width=1)
        chat_log.can_focus = False
        yield chat_log
        yield ThinkingIndicator(id="chat-thinking")
        yield Input(placeholder="Ask about this pattern…", id="chat-input")

    def set_topic(self, topic: dict) -> None:
        self._topic = topic

    def reset(self) -> None:
        self.query_one("#chat-log", RichLog).clear()

    def focus_input(self) -> None:
        self.query_one("#chat-input", Input).focus()

    def set_busy(self, busy: bool) -> None:
        self.query_one("#chat-input", Input).disabled = busy
        self.query_one("#chat-thinking", ThinkingIndicator).display = busy

    def append_user(self, message: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(Panel(
            _esc(message),
            title=f"[bold {AMBER}] you [/bold {AMBER}]",
            title_align="left",
            border_style=AMBER,
            padding=(0, 1),
            expand=True,
        ))
        log.scroll_end(animate=False)

    def append_ai(self, content: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(Panel(
            Text.from_markup(_render_response_to_markup(content)),
            title=f"[bold {FIRE}] vibe [/bold {FIRE}]",
            title_align="left",
            border_style=FIRE,
            padding=(0, 1),
            expand=True,
        ))
        log.scroll_end(animate=False)

    def append_error(self, message: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(Panel(
            f"[{RED}]{_esc(message)}[/{RED}]",
            title=f"[bold {RED}] error [/bold {RED}]",
            title_align="left",
            border_style=RED,
            padding=(0, 1),
            expand=True,
        ))
        log.scroll_end(animate=False)

    def append_raw(self, line: str) -> None:
        self.query_one("#chat-log", RichLog).write(line)

    def restore_history(self, messages: list[dict]) -> None:
        """Re-render a saved conversation history into the log."""
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        for msg in messages:
            if msg["role"] == "user":
                self.append_user(msg["content"])
            elif msg["role"] == "assistant":
                self.append_ai(msg["content"])

    def on_key(self, event: Key) -> None:
        if event.key == "space":
            inp = self.query_one("#chat-input", Input)
            if inp.has_focus and not inp.disabled:
                inp.insert_text_at_cursor(" ")
                event.prevent_default()
                event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "chat-expand":
            self.toggle_class("expanded")
            btn = self.query_one("#chat-expand", Button)
            if "expanded" in self.classes:
                btn.label = "▶"
                btn.tooltip = "Collapse chat panel"
            else:
                btn.label = "◀"
                btn.tooltip = "Expand chat panel"
            event.stop()
            self.post_message(self.Toggled())
            self.call_after_refresh(self.focus_input)
        elif event.button.id == "chat-reset":
            self.reset()
            self.post_message(self.Cleared())
            self.focus_input()


# ── Inline notes panel ────────────────────────────────────────────────────────

class NotesPanel(Widget):
    """Inline notes editor — slides in below content when N is pressed."""

    class Closed(Message):
        """Posted when the panel is closed, carrying the saved text."""
        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    def compose(self) -> ComposeResult:
        yield Static(
            f"[{DIM}]✎  Type your notes — press Esc to save & close[/{DIM}]",
            id="notes-hint",
            markup=True,
        )
        yield TextArea("", id="notes-textarea", show_line_numbers=False)

    def load(self, note: str) -> None:
        ta = self.query_one("#notes-textarea", TextArea)
        ta.load_text(note)
        self.call_after_refresh(ta.focus)

    def get_text(self) -> str:
        return self.query_one("#notes-textarea", TextArea).text

    def on_key(self, event: Key) -> None:
        ta = self.query_one("#notes-textarea", TextArea)
        if event.key == "space" and ta.has_focus:
            ta.insert(" ")
            event.prevent_default()
            event.stop()
        elif event.key == "escape":
            self.post_message(self.Closed(self.get_text()))
            event.stop()


# ── Filter helpers ─────────────────────────────────────────────────────────────

# All topic titles that belong to a named category group
_CAT_TOPIC_SET = {name for cat in CATEGORIES for name in cat["topics"]}


def _trunc(text: str, max_chars: int) -> str:
    if len(text) > max_chars:
        return text[: max_chars - 1] + "…"
    return text

_CAT_OPTIONS  = [("All Categories", "all")] + [(c["name"], c["name"]) for c in CATEGORIES]
_TIER_OPTIONS = [
    ("All Tiers",        "all"),
    ("Foundational",  "1"),
    ("Intermediate",  "2"),
    ("Advanced",      "3"),
]


# ── Screen ─────────────────────────────────────────────────────────────────────

class ReferenceGuideScreen(BaseScreen):
    """Playbook mode — browse algorithm topics, add notes, and export to DOCX."""

    BINDINGS = [
        Binding("escape",  "pop_screen",      "← Back"),
        Binding("ctrl+q",  "quit_app",        "Quit"),
        Binding("e",       "explain_more",    "Explain More", show=False),
        Binding("p",       "practice",        "Practice",     show=False),
        Binding("n",       "edit_note",       "Edit Note",    show=False),
        Binding("x",       "export_docx",     "Export DOCX",  show=False),
    ]

    filter_cat:   reactive[str] = reactive("all")
    filter_tier:  reactive[str] = reactive("all")
    search_query: reactive[str] = reactive("")

    def __init__(self) -> None:
        super().__init__()
        self._current_idx: int = 0
        self._notes: dict[str, str] = {}
        self._chat_open: bool = False
        self._notes_open: bool = False
        self._streaming: bool = False
        self._histories: dict[str, list[dict]] = {}
        self._option_map: list[int | None] = []  # OptionList pos → _visible_topics idx

    # ── Filtered topic list ──────────────────────────────────────────────

    @property
    def _visible_topics(self) -> list[dict]:
        result = list(TOPICS)
        if self.filter_cat != "all":
            result = [t for t in result if t.get("category") == self.filter_cat]
        if self.filter_tier != "all":
            result = [t for t in result if t.get("tier") == int(self.filter_tier)]
        q = self.search_query.strip().lower()
        if q:
            result = [t for t in result if q in t["title"].lower()]
        return result

    def compose(self) -> ComposeResult:
        with Horizontal(id="ref-filter-bar"):
            yield TruncatedSelect(_CAT_OPTIONS,  value="all", id="cat-filter",  allow_blank=False)
            yield TruncatedSelect(_TIER_OPTIONS, value="all", id="tier-filter", allow_blank=False)
            yield Input(placeholder="Search topic…", id="topic-search")
        with Horizontal(id="ref-body"):
            with Vertical(id="ref-topics"):
                yield OptionList(id="topic-list")
            with Vertical(id="ref-center"):
                with VerticalScroll(id="ref-content-scroll"):
                    yield Static("", id="ref-content-title", markup=True)
                    yield Static("", id="ref-content-body", markup=True)
                yield NotesPanel(id="notes-panel")
            yield PlaybookChatPanel(id="chat-panel")

        yield StatusBar(
            hints=[
                ("↑↓",     "navigate",         None),
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
        self._histories = _load_histories()
        self._rebuild_list()

    # ── Reactive filter watchers ─────────────────────────────────────────

    def watch_filter_cat(self, value: str) -> None:
        try:
            self.query_one("#cat-filter", TruncatedSelect).set_class(value != "all", "filter-active")
            self._rebuild_list()
        except Exception:
            pass

    def watch_filter_tier(self, value: str) -> None:
        try:
            self.query_one("#tier-filter", TruncatedSelect).set_class(value != "all", "filter-active")
            self._rebuild_list()
        except Exception:
            pass

    def watch_search_query(self, value: str) -> None:
        try:
            self.query_one("#topic-search", Input).set_class(bool(value.strip()), "filter-active")
            self._rebuild_list()
        except Exception:
            pass

    def on_resize(self) -> None:
        self._rebuild_list(refocus=False)
        if self._chat_open and not self._streaming:
            if getattr(self, "_chat_resize_timer", None) is not None:
                self._chat_resize_timer.stop()
            self._chat_resize_timer = self.set_timer(0.15, self._rerender_chat)

    def _rerender_chat(self) -> None:
        self._chat_resize_timer = None
        if not self._chat_open or self._streaming:
            return
        visible = self._visible_topics
        if not visible:
            return
        slug = visible[self._current_idx]["slug"]
        panel = self.query_one(PlaybookChatPanel)
        panel.restore_history(self._histories.get(slug, []))

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "cat-filter":
            self.filter_cat = str(event.value)
        elif event.select.id == "tier-filter":
            self.filter_tier = str(event.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "topic-search":
            self._pending_search = event.value
            if getattr(self, "_search_timer", None) is not None:
                self._search_timer.stop()
            self._search_timer = self.set_timer(0.2, self._apply_search)

    def _apply_search(self) -> None:
        self._search_timer = None
        self.search_query = getattr(self, "_pending_search", "")


    def _sidebar_max_chars(self) -> int:
        try:
            w = self.query_one("#ref-topics").size.width
            return max(10, w - 4)  # subtract border (2) + padding (2)
        except Exception:
            return 24

    def _rebuild_list(self, *, refocus: bool = True) -> None:
        """Repopulate the OptionList from _visible_topics and reset selection."""
        visible = self._visible_topics
        topic_list = self.query_one("#topic-list", OptionList)
        topic_list.clear_options()
        self._option_map = []

        if self.filter_cat == "all":
            max_w = self._sidebar_max_chars()
            # Ungrouped items first (Pattern Selector / anything without a category group)
            for i, t in enumerate(visible):
                if t["title"] not in _CAT_TOPIC_SET:
                    topic_list.add_option(Option(_trunc(t["title"], max_w), id=f"topic-{i}"))
                    self._option_map.append(i)

            # Grouped categories in CATEGORIES order
            for cat in CATEGORIES:
                cat_visible: list[tuple[int, dict]] = []
                for title in cat["topics"]:
                    for i, t in enumerate(visible):
                        if t["title"] == title:
                            cat_visible.append((i, t))
                            break
                if not cat_visible:
                    continue
                safe_id = cat["name"].replace(" ", "-").replace("&", "and").replace("/", "-")
                topic_list.add_option(
                    Option(_trunc(f"{cat['icon']}  {cat['name']}", max_w), id=f"cat-{safe_id}", disabled=True)
                )
                self._option_map.append(None)
                for i, t in cat_visible:
                    label = "  " + _trunc(t["title"], max_w - 2)
                    topic_list.add_option(Option(label, id=f"topic-{i}"))
                    self._option_map.append(i)
        else:
            max_w = self._sidebar_max_chars()
            # Single category filtered — flat list
            for i, t in enumerate(visible):
                topic_list.add_option(Option(_trunc(t["title"], max_w), id=f"topic-{i}"))
                self._option_map.append(i)

        # Select first non-header option
        first_pos = next((p for p, ti in enumerate(self._option_map) if ti is not None), 0)
        self._current_idx = self._option_map[first_pos] if self._option_map else 0
        if self._option_map:
            topic_list.highlighted = first_pos
        self._refresh_content()
        if refocus:
            topic_list.focus()

    # ── Topic navigation ─────────────────────────────────────────────────

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        pos = event.option_index
        topic_idx = self._option_map[pos] if pos < len(self._option_map) else None
        if topic_idx is None:
            return  # header row — ignore

        visible = self._visible_topics

        if self._notes_open and visible:
            prev_slug = visible[self._current_idx]["slug"]
            self._save_note(prev_slug, self.query_one(NotesPanel).get_text())

        self._current_idx = topic_idx
        self._refresh_content()

        if self._notes_open and visible:
            topic = visible[self._current_idx]
            self.query_one(NotesPanel).load(self._notes.get(topic["slug"], ""))

        if self._chat_open and not self._streaming:
            if visible:
                topic = visible[self._current_idx]
                panel = self.query_one(PlaybookChatPanel)
                panel.set_topic(topic)
                slug = topic["slug"]
                panel.restore_history(self._histories.get(slug, []))

    def _refresh_content(self) -> None:
        visible = self._visible_topics
        if not visible:
            try:
                self.query_one("#ref-content-title", Static).update("")
                self.query_one("#ref-content-body", Static).update(
                    f"\n  [{DIM}]No topics match the current filters.[/{DIM}]"
                )
            except Exception:
                pass
            return
        topic = visible[self._current_idx]
        note  = self._notes.get(topic["slug"], "")
        try:
            self.query_one("#ref-content-title", Static).update(_render_title(topic["title"]))
            self.query_one("#ref-content-body", Static).update(_render_topic(topic, note))
            self.query_one("#ref-content-scroll", VerticalScroll).scroll_home(animate=False)
        except Exception:
            pass

    # ── Actions ──────────────────────────────────────────────────────────

    def action_pop_screen(self) -> None:
        if self._chat_open:
            self.action_explain_more()
        elif self._notes_open:
            self.action_edit_note()
        else:
            self.app.pop_screen()

    def _save_note(self, slug: str, text: str) -> None:
        self._notes[slug] = text
        _save_notes(self._notes)
        self._refresh_content()

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
            panel.restore_history(self._histories.get(topic["slug"], []))
            panel.add_class("open")
            self._chat_open = True
            self.call_after_refresh(panel.focus_input)

    def on_playbook_chat_panel_toggled(self, _event: PlaybookChatPanel.Toggled) -> None:
        self.call_after_refresh(self._rerender_chat)

    def on_playbook_chat_panel_cleared(self, _event: PlaybookChatPanel.Cleared) -> None:
        """Clear saved history for the current topic when user resets chat."""
        visible = self._visible_topics
        if not visible:
            return
        slug = visible[self._current_idx]["slug"]
        self._histories.pop(slug, None)
        _save_histories(self._histories)

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
        slug  = topic["slug"]

        self._streaming = True
        self.app.call_from_thread(panel.set_busy, True)

        history = self._histories.setdefault(slug, [])
        history.append({"role": "user", "content": user_message})

        system_prompt = (
            "You are Vibe, a concise algorithm tutor inside LeetVibe. "
            "Answer questions about the current pattern clearly and briefly. "
            "Use **bold** for key terms and ``` for code blocks.\n\n"
            f"=== Pattern Reference ===\n{_build_topic_context(topic)}"
        )

        try:
            from mistralai import Mistral
            from ...config import load_config

            config = load_config()
            client = Mistral(api_key=config.mistral_api_key)

            full_response = ""

            with client.chat.stream(
                model=config.mistral_qa_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *history[:-1][-10:],  # last 10 prior turns; full history kept on disk
                    {"role": "user", "content": user_message},
                ],
            ) as stream:
                for event in stream:
                    try:
                        chunk = event.data.choices[0].delta.content or ""
                    except (AttributeError, IndexError):
                        continue
                    full_response += chunk

            if full_response.strip():
                self.app.call_from_thread(panel.append_ai, full_response)

            history.append({"role": "assistant", "content": full_response})
            _save_histories(self._histories)

        except Exception as exc:
            history.pop()
            self.app.call_from_thread(panel.append_error, str(exc)[:120])
        finally:
            self._streaming = False
            self.app.call_from_thread(panel.set_busy, False)

    def action_practice(self) -> None:
        """Open problem list pre-filtered to the current topic."""
        visible = self._visible_topics
        if not visible:
            return
        topic = visible[self._current_idx]
        self._open_practice(topic)

    @work(thread=True)
    def _open_practice(self, topic: dict) -> None:
        slug = topic["slug"]
        if slug not in _get_db_topic_slugs():
            self.app.call_from_thread(
                self.notify,
                f"No problems tagged for '{topic['title']}' yet.",
                severity="warning",
            )
            return
        from .problem_list import ProblemListScreen
        self.app.call_from_thread(
            self.app.push_screen,
            ProblemListScreen(mode="learn", initial_topic=slug),
        )

    def action_edit_note(self) -> None:
        """Toggle the inline notes panel for the current topic."""
        visible = self._visible_topics
        if not visible:
            return
        topic = visible[self._current_idx]
        panel = self.query_one(NotesPanel)
        if self._notes_open:
            self._save_note(topic["slug"], panel.get_text())
            panel.remove_class("open")
            self._notes_open = False
            self.query_one("#topic-list", OptionList).focus()
        else:
            panel.load(self._notes.get(topic["slug"], ""))
            panel.add_class("open")
            self._notes_open = True

    def on_notes_panel_closed(self, event: NotesPanel.Closed) -> None:
        visible = self._visible_topics
        if visible:
            self._save_note(visible[self._current_idx]["slug"], event.text)
        self.query_one(NotesPanel).remove_class("open")
        self._notes_open = False
        self.query_one("#topic-list", OptionList).focus()

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
