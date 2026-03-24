"""One-time onboarding wizard — collects MISTRAL_API_KEY on first run."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from .screens.onboarding import (
    WelcomeScreen,
    ApiKeyScreen,
    ElevenLabsKeyScreen,
    AuthChoiceScreen,
    LoginScreen,
    SignupScreen,
    GoogleAuthScreen,
)

__all__ = [
    "run_onboarding",
    "WelcomeScreen",
    "ApiKeyScreen",
    "ElevenLabsKeyScreen",
    "AuthChoiceScreen",
    "LoginScreen",
    "SignupScreen",
    "GoogleAuthScreen",
]


class OnboardingApp(App[str | None]):
    CSS_PATH = Path(__file__).parent / "setup.tcss"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())


def run_onboarding() -> bool:
    """Run the onboarding wizard. Returns True if completed, False if cancelled."""
    return OnboardingApp().run() == "completed"
