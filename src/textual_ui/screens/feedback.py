"""FeedbackModal — modal dialog for submitting user feedback."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, TextArea


_FEEDBACK_TYPES = [
    ("Bug report",       "bug_report"),
    ("Feature request",  "feature_request"),
    ("Content issue",    "content_issue"),
    ("General feedback", "general"),
]


class FeedbackModal(ModalScreen[bool]):
    """Modal for submitting feedback about a specific challenge."""

    DEFAULT_CSS = """
    FeedbackModal {
        align: center middle;
    }

    #feedback-dialog {
        width: 70;
        height: auto;
        background: #1a1a1a;
        border: round #FF8205;
        padding: 2 3;
    }

    #feedback-title {
        color: #FF8205;
        text-style: bold;
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }

    #feedback-type-label {
        color: #888888;
        margin-bottom: 0;
    }

    #feedback-type {
        width: 100%;
        margin-bottom: 1;
    }

    #feedback-msg-label {
        color: #888888;
        margin-bottom: 0;
    }

    #feedback-text {
        width: 100%;
        height: 8;
        border: tall #444444;
        background: #121212;
        margin-bottom: 1;
    }

    #feedback-text:focus {
        border: tall #FF8205;
    }

    #feedback-error {
        color: #ff4444;
        height: 1;
        width: 100%;
        text-align: center;
    }

    #feedback-buttons {
        width: 100%;
        height: auto;
        align: right middle;
        margin-top: 1;
    }

    #btn-feedback-cancel {
        border: none;
        background: transparent;
        color: #888888;
        margin-right: 1;
    }

    #btn-feedback-cancel:hover {
        color: #e0e0e0;
    }

    #btn-feedback-submit {
        border: tall #FF8205;
        background: transparent;
        color: #FF8205;
    }

    #btn-feedback-submit:hover {
        background: #3a2200;
    }

    #btn-feedback-submit:disabled {
        color: #444444;
        border: tall #333333;
    }
    """

    def __init__(
        self,
        problem_slug: str | None = None,
        session_id: str | None = None,
    ) -> None:
        super().__init__()
        self._problem_slug = problem_slug
        self._session_id = session_id

    def compose(self) -> ComposeResult:
        with Vertical(id="feedback-dialog"):
            yield Label("Send Feedback", id="feedback-title")
            yield Label("Type", id="feedback-type-label")
            yield Select(
                _FEEDBACK_TYPES,
                value="general",
                allow_blank=False,
                id="feedback-type",
            )
            yield Label("Message", id="feedback-msg-label")
            yield TextArea(id="feedback-text")
            yield Label("", id="feedback-error")
            with Horizontal(id="feedback-buttons"):
                yield Button("Cancel", id="btn-feedback-cancel")
                yield Button("Submit", id="btn-feedback-submit")

    def on_mount(self) -> None:
        self.query_one("#feedback-text", TextArea).focus()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-feedback-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-feedback-submit":
            self._submit()

    def _submit(self) -> None:
        message = self.query_one("#feedback-text", TextArea).text.strip()
        if not message:
            self.query_one("#feedback-error", Label).update("Please enter a message.")
            return
        feedback_type = str(self.query_one("#feedback-type", Select).value)
        self.query_one("#btn-feedback-submit", Button).disabled = True
        self.query_one("#feedback-error", Label).update("Sending…")
        self._send_feedback(feedback_type, message)

    @work(thread=True)
    def _send_feedback(self, feedback_type: str, message: str) -> None:
        from ...cloud.db import submit_feedback

        ok = submit_feedback(
            type=feedback_type,
            message=message,
            problem_slug=self._problem_slug,
            session_id=self._session_id,
        )
        self.app.call_from_thread(self._on_sent, ok)

    def _on_sent(self, ok: bool) -> None:
        if ok:
            self.dismiss(True)
        else:
            try:
                self.query_one("#btn-feedback-submit", Button).disabled = False
                self.query_one("#feedback-error", Label).update(
                    "Failed to send. Please try again."
                )
            except Exception:
                pass
