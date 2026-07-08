"""Terminal key-handling quirks shared across text-input widgets."""

from __future__ import annotations

from textual.events import Key
from textual.widgets import Input, TextArea


def reinsert_swallowed_space(event: Key, widget: Input | TextArea) -> None:
    """Some terminals swallow the space key before it reaches a focused
    Input/TextArea — detect that case and insert it manually.

    Safe to call unconditionally from a screen/widget's on_key(): a no-op
    unless the key is space, *widget* is focused, and (for Input) not disabled.
    """
    if event.key != "space" or not widget.has_focus:
        return
    if isinstance(widget, Input) and widget.disabled:
        return
    if isinstance(widget, TextArea):
        widget.insert(" ")
    else:
        widget.insert_text_at_cursor(" ")
    event.prevent_default()
    event.stop()
