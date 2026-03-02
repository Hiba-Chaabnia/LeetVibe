"""Preview HomeScreen in isolation.

Run with:
    textual run --dev dev/preview_home.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App
from src.textual_ui.screens.home import HomeScreen


class PreviewApp(App):
    CSS_PATH = Path(__file__).parent.parent / "src/textual_ui/app.tcss"

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


if __name__ == "__main__":
    PreviewApp().run()
