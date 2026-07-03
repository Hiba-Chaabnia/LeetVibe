"""PlaybookScreen — Playbook mode: algorithm topics with notes and export."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input, OptionList, Select, Static
from textual.widgets.option_list import Option

from leetvibe.data.topics import CATEGORIES, TOPICS
from leetvibe.ui.theme import DIM
from leetvibe.ui.widgets import StatusBar, TruncatedSelect
from leetvibe.ui.screens.base import BaseScreen

from .panels import NotesPanel, PlaybookChatPanel
from .render import (
    build_topic_context,
    load_histories,
    load_notes,
    render_title,
    render_topic,
    save_histories,
    save_notes,
)

# ── Database topic slug cache ──────────────────────────────────────────────────

_DB_TOPIC_SLUGS: set[str] | None = None


def _get_db_topic_slugs() -> set[str]:
    """Return the set of topic tags that exist in the problems database (cached)."""
    global _DB_TOPIC_SLUGS
    if _DB_TOPIC_SLUGS is None:
        from leetvibe.problem_loader import load_all_problems
        problems = load_all_problems()
        _DB_TOPIC_SLUGS = {t for ch in problems for t in (ch.topics or [])}
    return _DB_TOPIC_SLUGS


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

class PlaybookScreen(BaseScreen):
    """Playbook mode — browse algorithm topics, add notes, and export to DOCX."""

    BINDINGS = [
        Binding("escape",  "pop_screen",      "← Back"),
        Binding("ctrl+q",  "quit_app",        "Quit"),
        Binding("ctrl+e",  "explain_more",    "Explain More", show=False, priority=True),
        Binding("ctrl+o",  "practice",        "Practice",     show=False),
        Binding("ctrl+n",  "edit_note",       "Edit Note",    show=False),
        Binding("ctrl+x",  "export_docx",     "Export DOCX",  show=False, priority=True),
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
                ("Ctrl+E", "ask AI",      self.action_explain_more),
                ("Ctrl+O", "open problems",    self.action_practice),
                ("Ctrl+N", "note it down",     self.action_edit_note),
                ("Ctrl+X", "export DOCX",      self.action_export_docx),
            ],
            id="ref-status",
        )

    def on_mount(self) -> None:
        self._notes = load_notes()
        self._histories = load_histories()
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
        """Repopulate the OptionList from _visible_topics, preserving the current topic."""
        visible = self._visible_topics
        current_slug = (
            visible[self._current_idx]["slug"]
            if visible and 0 <= self._current_idx < len(visible)
            else None
        )
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

        # Re-select the same topic as before the rebuild, if it's still visible;
        # otherwise fall back to the first non-header option.
        first_pos = next((p for p, ti in enumerate(self._option_map) if ti is not None), 0)
        target_pos = first_pos
        if current_slug is not None:
            target_pos = next(
                (
                    p for p, ti in enumerate(self._option_map)
                    if ti is not None and visible[ti]["slug"] == current_slug
                ),
                first_pos,
            )
        self._current_idx = self._option_map[target_pos] if self._option_map else 0
        if self._option_map:
            topic_list.highlighted = target_pos
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
            self.query_one("#ref-content-title", Static).update(render_title(topic["title"]))
            self.query_one("#ref-content-body", Static).update(render_topic(topic, note))
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
        save_notes(self._notes)
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
            panel.add_class("open")
            self._chat_open = True
            # Panel is `display: none` until the "open" class is applied above, so its
            # RichLog has no real width yet — defer the restore until after layout runs,
            # otherwise the history bakes in at a stale/collapsed width.
            self.call_after_refresh(panel.restore_history, self._histories.get(topic["slug"], []))
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
        save_histories(self._histories)

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
            f"=== Pattern Reference ===\n{build_topic_context(topic)}"
        )

        try:
            from mistralai import Mistral
            from leetvibe.config import load_config

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
            save_histories(self._histories)

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
        from leetvibe.ui.screens.problem.list import ProblemListScreen
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
            from leetvibe.docx_exporter import export_reference_docx
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
