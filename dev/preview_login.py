"""Preview LoginScreen in isolation.

Run with:
    textual run --dev dev/preview_login.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App
from src.textual_ui.screens.login import LoginScreen


class PreviewApp(App):
    CSS_PATH = Path(__file__).parent.parent / "src/textual_ui/app.tcss"

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())


if __name__ == "__main__":
    PreviewApp().run()
