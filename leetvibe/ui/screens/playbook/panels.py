"""Playbook side panels — inline AI chat, notes editor."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Static, TextArea

from leetvibe.ui.keys import reinsert_swallowed_space
from leetvibe.ui.theme import DIM
from leetvibe.ui.widgets import ChatBubbleLog, ThinkingIndicator

from .render import render_response_to_markup


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
            reset_btn = Button("↺", id="chat-reset", classes="chat-reset-btn")
            reset_btn.tooltip = "Clear chat history"
            reset_btn.can_focus = False
            yield reset_btn
        chat_log = ChatBubbleLog(
            id="chat-log",
            renderer=render_response_to_markup,
            markup=True, wrap=True, highlight=False, min_width=1,
        )
        chat_log.can_focus = False
        yield chat_log
        yield ThinkingIndicator(id="chat-thinking")
        yield Input(placeholder="Ask about this pattern…", id="chat-input")

    def _log(self) -> ChatBubbleLog:
        return self.query_one("#chat-log", ChatBubbleLog)

    def set_topic(self, topic: dict) -> None:
        self._topic = topic

    def reset(self) -> None:
        self._log().clear()

    def focus_input(self) -> None:
        self.query_one("#chat-input", Input).focus()

    def set_busy(self, busy: bool) -> None:
        self.query_one("#chat-input", Input).disabled = busy
        self.query_one("#chat-thinking", ThinkingIndicator).display = busy

    def append_user(self, message: str) -> None:
        self._log().append_user(message)

    def append_ai(self, content: str) -> None:
        self._log().append_ai(content)

    def append_error(self, message: str) -> None:
        self._log().append_error(message)

    def append_raw(self, line: str) -> None:
        self._log().append_raw(line)

    def restore_history(self, messages: list[dict]) -> None:
        """Re-render a saved conversation history into the log."""
        self._log().restore_history(messages)

    def on_key(self, event: Key) -> None:
        reinsert_swallowed_space(event, self.query_one("#chat-input", Input))

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
        reinsert_swallowed_space(event, self.query_one("#notes-textarea", TextArea))
        if event.key == "escape":
            self.post_message(self.Closed(self.get_text()))
            event.stop()
