"""One-time onboarding wizard — collects MISTRAL_API_KEY on first run."""

from __future__ import annotations

from textual.app import App

from .screens import (
    WelcomeScreen,
    ApiKeyScreen,
    AuthChoiceScreen,
    LoginScreen,
    SignupScreen,
    GoogleAuthScreen,
)

__all__ = [
    "run_onboarding",
    "WelcomeScreen",
    "ApiKeyScreen",
    "AuthChoiceScreen",
    "LoginScreen",
    "SignupScreen",
    "GoogleAuthScreen",
]

_CSS = """
Screen {
    background: #0f0f0f;
    align: center middle;
}

/* ── Welcome ── */

#welcome-container {
    width: auto;
    height: auto;
    align: center middle;
    padding: 2 4;
}

#hint {
    color: #888888;
    text-align: center;
    width: 100%;
    margin-top: 2;
}

/* ── API key ── */

#api-container {
    width: 60;
    height: auto;
    padding: 2 4;
}

#instruction {
    color: #cccccc;
    text-align: center;
    width: 100%;
    margin-bottom: 1;
}

#link-hint {
    color: #888888;
    text-align: center;
    width: 100%;
    margin-bottom: 2;
}

#api-key-input {
    width: 100%;
    border: tall #444444;
    background: #1a1a1a;
    color: #ffffff;
    margin-bottom: 1;
}

#api-key-input:focus {
    border: tall #FF8205;
}

#error-label {
    color: #ff4444;
    text-align: center;
    width: 100%;
    height: 1;
}

#submit-hint {
    color: #888888;
    text-align: center;
    width: 100%;
    margin-top: 1;
}

/* ── Auth choice ── */

#auth-container {
    width: 64;
    height: auto;
    padding: 2 4;
}

#auth-notice {
    color: #cccccc;
    text-align: center;
    width: 100%;
    margin-bottom: 1;
}

#auth-detail {
    color: #888888;
    text-align: center;
    width: 100%;
    margin-bottom: 2;
}

#auth-menu {
    width: 100%;
    height: auto;
    border: tall #333333;
    background: #111111;
}

/* ── Login / Signup ── */

#form-container {
    width: 60;
    height: auto;
    padding: 2 4;
}

#form-title {
    color: #FF8205;
    text-style: bold;
    text-align: center;
    width: 100%;
    margin-bottom: 2;
}

.form-input {
    width: 100%;
    border: tall #444444;
    background: #1a1a1a;
    color: #ffffff;
    margin-bottom: 1;
}

.form-input:focus {
    border: tall #FF8205;
}

#form-error {
    color: #ff4444;
    text-align: center;
    width: 100%;
    height: 1;
}

#form-hint {
    color: #888888;
    text-align: center;
    width: 100%;
    margin-top: 1;
}
"""


class OnboardingApp(App[str | None]):
    CSS = _CSS

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())


def run_onboarding() -> bool:
    """Run the onboarding wizard. Returns True if completed, False if cancelled."""
    return OnboardingApp().run() == "completed"
