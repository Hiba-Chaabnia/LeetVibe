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
from textual.reactive import reactive
from textual.widgets import Input, OptionList, RichLog, Select, Static
from textual.widgets.option_list import Option

from ...data.topics import CATEGORIES, TIER_MAP, TOPICS
from ..theme import AMBER, DIM, EMBER, FIRE, GOLD, GRADIENT, GREEN, LAVA, RED
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


def _code_block(block: str) -> list[str]:
    """Render a code block with box-drawing header and │-prefixed lines."""
    lines = [f"  [{DIM}]┌── python {'─' * 30}[/{DIM}]"]
    for ln in block.split("\n"):
        lines.append(f"  [{DIM}]│[/{DIM}] {ln}")
    lines.append(f"  [{DIM}]└{'─' * 41}[/{DIM}]")
    return lines


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
            f"  [{DIM}]{_esc(topic['when'])}[/{DIM}]",
        ]
        return "\n".join(lines)

    diagram  = _esc(topic.get("diagram", ""))
    when     = _esc(topic.get("when", ""))
    t_val    = _esc(topic.get("time", ""))
    s_val     = _esc(topic.get("space", ""))
    recognize = _esc(topic.get("recognize", ""))
    pitfalls  = _esc(topic.get("pitfalls", ""))
    related   = topic.get("related", [])

    lines: list[str] = [""]
    h = 0  # gradient index for section headers

    # Recognised by
    if recognize:
        lines.append(_sh("Recognised by", h)); h += 1
        for ln in recognize.split("\n"):
            lines.append(f"  [{DIM}]{ln}[/{DIM}]")
        lines.append("")

    # Diagram
    lines.append(_sh("Diagram", h)); h += 1
    lines += _infobox(diagram)
    lines.append("")

    # When to use
    lines.append(_sh("When to use", h)); h += 1
    lines += _infobox(when)
    lines.append("")

    # Patterns
    patterns = topic.get("patterns", [])
    if patterns:
        lines.append(_sh("Patterns", h)); h += 1
        for i, pat in enumerate(patterns, 1):
            lines.append(f"  [bold #ffffff]{i}. {_esc(pat['name'])}[/bold #ffffff]")
            lines += _code_block(_esc(pat["code"]))
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
        Binding("escape",  "pop_screen",   "← Back"),
        Binding("ctrl+q",  "quit_app",     "Quit"),
        Binding("e",       "explain_more", "Explain More", show=False),
        Binding("p",       "practice",     "Practice",     show=False),
        Binding("n",       "edit_note",    "Edit Note",    show=False),
        Binding("x",       "export_docx",  "Export DOCX",  show=False),
    ]

    filter_cat:   reactive[str] = reactive("all")
    filter_tier:  reactive[str] = reactive("all")
    search_query: reactive[str] = reactive("")

    def __init__(self) -> None:
        super().__init__()
        self._current_idx: int = 0
        self._notes: dict[str, str] = {}
        self._chat_open: bool = False
        self._chat_history: list[dict] = []
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
            with VerticalScroll(id="ref-content-scroll"):
                yield Static("", id="ref-content-title", markup=True)
                yield Static("", id="ref-content-body", markup=True)
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
        self._rebuild_list()

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

    def _rebuild_list(self) -> None:
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
        topic_list.focus()

    # ── Topic navigation ─────────────────────────────────────────────────

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        pos = event.option_index
        topic_idx = self._option_map[pos] if pos < len(self._option_map) else None
        if topic_idx is None:
            return  # header row — ignore
        self._current_idx = topic_idx
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
