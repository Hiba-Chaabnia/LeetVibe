"""FeedbackModal — modal dialog for submitting user feedback."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, TextArea

from ..widgets.shimmer_title import ShimmerTitle


# All types accepted by the feedback table CHECK constraint (001_initial_schema.sql)
_FEEDBACK_TYPES: list[tuple[str, str]] = [
    ("Bug report",           "bug"),
    ("Wrong solution",       "wrong_solution"),
    ("Wrong complexity",     "wrong_complexity"),
    ("Poor explanation",     "poor_explanation"),
    ("False test result",    "false_test_result"),
    ("Feature request",      "feature_request"),
    ("UI issue",             "ui_issue"),
    ("General feedback",     "general"),
    ("Praise / compliment",  "praise"),
]

_DEFAULT_TYPE = "general"


class FeedbackModal(ModalScreen[bool]):
    """Modal for submitting feedback about a specific problem."""

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
            yield ShimmerTitle("Send Feedback", id="feedback-title")
            yield Label("Type", id="feedback-type-label")
            yield Select(
                _FEEDBACK_TYPES,
                value=_DEFAULT_TYPE,
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

    def _get_feedback_type(self) -> str:
        """Return the selected feedback type, falling back to the default."""
        sel = self.query_one("#feedback-type", Select)
        # Guard against Select.BLANK sentinel (returned when no selection made)
        if sel.value is Select.BLANK:
            return _DEFAULT_TYPE
        return str(sel.value)

    def _submit(self) -> None:
        message = self.query_one("#feedback-text", TextArea).text.strip()
        if not message:
            self.query_one("#feedback-error", Label).update("Please enter a message.")
            return
        feedback_type = self._get_feedback_type()
        self.query_one("#btn-feedback-submit", Button).disabled = True
        self.query_one("#feedback-error", Label).update("Sending…")
        self._send_feedback(feedback_type, message)

    @work(thread=True)
    def _send_feedback(self, feedback_type: str, message: str) -> str | None:
        from ...cloud.db import submit_feedback

        return submit_feedback(
            type=feedback_type,
            message=message,
            problem_slug=self._problem_slug,
            session_id=self._session_id,
        )

    def on_worker_state_changed(self, event) -> None:
        from textual.worker import WorkerState

        if event.worker.name != "_send_feedback":
            return
        # on_worker_state_changed runs on the main thread — call directly
        if event.state == WorkerState.SUCCESS:
            self._on_sent(event.worker.result)
        elif event.state == WorkerState.ERROR:
            self._on_sent(f"Worker error: {event.worker.error}")

    def _on_sent(self, error: str | None) -> None:
        if error is None:
            self.dismiss(True)
        else:
            try:
                self.query_one("#btn-feedback-submit", Button).disabled = False
                # Show the actual error so it's debuggable
                self.query_one("#feedback-error", Label).update(
                    f"Error: {error}"
                )
            except Exception:
                pass
