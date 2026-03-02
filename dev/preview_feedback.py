"""Preview FeedbackModal in isolation (overlaid on a dummy background).

Run with:
    textual run --dev dev/preview_feedback.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App, ComposeResult
from textual.widgets import Static
from src.textual_ui.screens.feedback import FeedbackModal


class PreviewApp(App):
    CSS_PATH = Path(__file__).parent.parent / "src/textual_ui/app.tcss"

    def compose(self) -> ComposeResult:
        # Dummy background so the modal overlay is visible
        yield Static("[ Background screen — modal is overlaid ]", id="bg")

    def on_mount(self) -> None:
        # problem_slug and session_id are optional
        self.push_screen(
            FeedbackModal(problem_slug="two-sum", session_id=None)
        )


if __name__ == "__main__":
    PreviewApp().run()
