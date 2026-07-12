"""One-time onboarding wizard — collects MISTRAL_API_KEY on first run."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from leetvibe.ui.screens.onboarding import WelcomeScreen

__all__ = ["OnboardingApp", "run_onboarding"]


class OnboardingApp(App[str | None]):
    CSS_PATH = Path(__file__).parent / "styles" / "onboarding.tcss"
    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())


def run_onboarding() -> bool:
    """Run the onboarding wizard. Returns True if completed, False if cancelled."""
    return OnboardingApp().run() == "completed"
