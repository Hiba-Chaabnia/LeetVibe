"""ConfirmModal — generic yes/no confirmation dialog."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ..widgets.shimmer_title import ShimmerTitle


class ConfirmModal(ModalScreen[bool]):
    """Modal asking the user to confirm or cancel an action. Dismisses with a bool."""

    def __init__(self, title: str, message: str, confirm_label: str = "Confirm") -> None:
        super().__init__()
        self._title_text = title
        self._message = message
        self._confirm_label = confirm_label

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield ShimmerTitle(self._title_text, id="confirm-title")
            yield Static(self._message, id="confirm-subtitle", markup=False)
            with Horizontal(id="confirm-buttons"):
                yield Button("Cancel", id="btn-confirm-cancel")
                yield Button(self._confirm_label, id="btn-confirm-yes")

    def on_mount(self) -> None:
        self.query_one("#btn-confirm-cancel", Button).focus()

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-confirm-yes")
