"""Preview ChallengeListScreen in isolation.

Run with:
    textual run --dev dev/preview_challenge_list.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App
from src.textual_ui.screens.challenge_list import ChallengeListScreen


class PreviewApp(App):
    CSS_PATH = Path(__file__).parent.parent / "src/textual_ui/app.tcss"

    def on_mount(self) -> None:
        # mode can be "learn" or "compete"
        self.push_screen(ChallengeListScreen(mode="learn"))


if __name__ == "__main__":
    PreviewApp().run()
