"""NotesModal — inline note editor for a reference topic."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static, TextArea

from ..theme import FIRE, GOLD


class NotesModal(ModalScreen[str | None]):
    """Modal for editing a note on a Concepts reference topic.

    Dismisses with the new note text (str) on save, or None on cancel.
    """

    BINDINGS = [
        Binding("ctrl+s", "save_note", "Save",   show=True),
        Binding("escape", "cancel",    "Cancel",  show=True),
    ]

    def __init__(self, topic_title: str, existing_note: str = "") -> None:
        super().__init__()
        self._topic_title = topic_title
        self._existing_note = existing_note

    def compose(self) -> ComposeResult:
        with Container(id="notes-dialog"):
            yield Static(f"Notes — {self._topic_title}", id="notes-title")
            yield Static("Markdown supported · Ctrl+S save · Esc cancel", id="notes-hint")
            yield TextArea(self._existing_note, id="notes-area")
            with Horizontal(id="notes-buttons"):
                yield Button("Cancel  [Esc]",    id="btn-cancel")
                yield Button("Save  [Ctrl+S]",   id="btn-save")

    def on_mount(self) -> None:
        self.query_one("#notes-area", TextArea).focus()

    # ── Actions ─────────────────────────────────────────────────────────

    def action_save_note(self) -> None:
        text = self.query_one("#notes-area", TextArea).text
        self.dismiss(text)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.action_save_note()
        else:
            self.action_cancel()
