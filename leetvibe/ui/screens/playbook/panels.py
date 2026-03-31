"""Playbook side panels — inline AI chat, notes editor, and thinking indicator."""

from __future__ import annotations

from rich.panel import Panel
from rich.text import Text

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, RichLog, Static, TextArea

from leetvibe.ui.theme import AMBER, DIM, FIRE, RED, SHIMMER

from .render import esc, render_response_to_markup

_SPINNER_FRAMES: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


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
            esc(message),
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
            Text.from_markup(render_response_to_markup(content)),
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
            f"[{RED}]{esc(message)}[/{RED}]",
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
