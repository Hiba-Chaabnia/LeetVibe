"""One-time onboarding wizard — collects MISTRAL_API_KEY on first run."""

from __future__ import annotations

import asyncio
import os
import webbrowser
from pathlib import Path

from dotenv import set_key
from textual import work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from ..textual_ui.widgets.banner import Banner


_LEETVIBE_HOME = Path.home() / ".leetvibe"
_USER_ENV_PATH = _LEETVIBE_HOME / ".env"

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


# ── Screens ───────────────────────────────────────────────────────────────────

class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="welcome-container"):
            yield Banner(id="welcome-banner")
            yield Label("Press Enter to continue", id="hint")

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.app.push_screen(ApiKeyScreen())
        elif event.key == "escape":
            self.app.exit(None)


class ApiKeyScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="api-container"):
            yield Label("Enter your Mistral API key to get started.", id="instruction")
            yield Label("Get one at: console.mistral.ai/codestral", id="link-hint")
            yield Input(password=True, placeholder="sk-...", id="api-key-input")
            yield Label("", id="error-label")
            yield Label("Enter to save  ·  Esc to cancel", id="submit-hint")

    def on_mount(self) -> None:
        self.query_one("#api-key-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save_key(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.exit(None)

    def _save_key(self, raw: str) -> None:
        key = raw.strip()
        if not key:
            self.query_one("#error-label", Label).update("Key cannot be empty.")
            return

        _LEETVIBE_HOME.mkdir(parents=True, exist_ok=True)
        set_key(str(_USER_ENV_PATH), "MISTRAL_API_KEY", key)
        os.environ["MISTRAL_API_KEY"] = key
        self.app.push_screen(AuthChoiceScreen())


class AuthChoiceScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="auth-container"):
            yield Label(
                "Want to keep your progress?",
                id="auth-notice",
            )
            yield Label(
                "Creating a free account lets you sync your solved problems\n"
                "across devices and reinstalls. You can always do this later.",
                id="auth-detail",
            )
            yield OptionList(
                Option("→  Sign In        I already have an account", id="login"),
                Option("✦  Create Account  Start syncing my progress", id="signup"),
                Option("G  Google          Sign in with Google", id="google"),
                Option("✕  Skip            Continue without an account", id="skip"),
                id="auth-menu",
            )

    def on_mount(self) -> None:
        self.query_one("#auth-menu", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        oid = event.option.id
        if oid == "skip":
            self.app.exit("completed")
        elif oid == "login":
            self.app.push_screen(LoginScreen())
        elif oid == "signup":
            self.app.push_screen(SignupScreen())
        elif oid == "google":
            self.app.push_screen(GoogleAuthScreen())

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.exit("completed")


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Sign In", id="form-title")
            yield Input(placeholder="Email", id="email-input", classes="form-input")
            yield Input(placeholder="Password", password=True, id="password-input", classes="form-input")
            yield Label("", id="form-error")
            yield Label("Tab to switch fields  ·  Enter to sign in  ·  Esc to go back", id="form-hint")

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "enter":
            email = self.query_one("#email-input", Input).value
            password = self.query_one("#password-input", Input).value
            self._submit(email, password)

    def _submit(self, email: str, password: str) -> None:
        email = email.strip()
        password = password.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        self._run_sign_in(email, password)

    @work
    async def _run_sign_in(self, email: str, password: str) -> None:
        from ..cloud.auth import sign_in
        self.query_one("#form-error", Label).update("Signing in…")
        result = await asyncio.to_thread(sign_in, email, password)
        if result.ok:
            self.app.exit("completed")
        else:
            self.query_one("#form-error", Label).update(result.error or "Sign in failed.")


class SignupScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Create Account", id="form-title")
            yield Input(placeholder="Email", id="email-input", classes="form-input")
            yield Input(placeholder="Password", password=True, id="password-input", classes="form-input")
            yield Input(placeholder="Confirm password", password=True, id="confirm-input", classes="form-input")
            yield Label("", id="form-error")
            yield Label("Tab to switch fields  ·  Enter to create  ·  Esc to go back", id="form-hint")

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "enter":
            email = self.query_one("#email-input", Input).value
            password = self.query_one("#password-input", Input).value
            confirm = self.query_one("#confirm-input", Input).value
            self._submit(email, password, confirm)

    def _submit(self, email: str, password: str, confirm: str) -> None:
        email = email.strip()
        password = password.strip()
        confirm = confirm.strip()
        if not email or not password:
            self.query_one("#form-error", Label).update("Email and password are required.")
            return
        if password != confirm:
            self.query_one("#form-error", Label).update("Passwords do not match.")
            return
        self._run_sign_up(email, password)

    @work
    async def _run_sign_up(self, email: str, password: str) -> None:
        from ..cloud.auth import sign_up
        self.query_one("#form-error", Label).update("Creating account…")
        result = await asyncio.to_thread(sign_up, email, password)
        if result.ok:
            if result.confirm_email:
                # Supabase sent a confirmation email — inform the user then continue
                self.query_one("#form-error", Label).update(
                    f"Check your inbox ({result.email}) to confirm your account."
                )
                await asyncio.sleep(3)
            self.app.exit("completed")
        else:
            self.query_one("#form-error", Label).update(result.error or "Sign up failed.")


class GoogleAuthScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Sign in with Google", id="form-title")
            yield Label("", id="form-error")
            yield Label("Esc to cancel", id="form-hint")

    def on_mount(self) -> None:
        self._run_google_auth()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

    @work
    async def _run_google_auth(self) -> None:
        from ..cloud.auth import start_google_auth, GoogleAuthState

        self.query_one("#form-error", Label).update("Opening your browser…")
        state = await asyncio.to_thread(start_google_auth)

        if not isinstance(state, GoogleAuthState):
            # start_google_auth returned an AuthResult(ok=False)
            self.query_one("#form-error", Label).update(state.error or "Google auth failed.")
            return

        webbrowser.open(state.oauth_url)
        self.query_one("#form-error", Label).update(
            "Waiting for Google sign-in in your browser…\n"
            "Switch back here once you've signed in."
        )

        # Block in a thread so the event loop stays free; 120 s timeout
        completed = await asyncio.to_thread(state.done.wait, 120)

        if not completed:
            self.query_one("#form-error", Label).update("Timed out. Press Esc and try again.")
            return

        result = state.result
        if result and result.ok:
            self.app.exit("completed")
        else:
            self.query_one("#form-error", Label).update(
                (result.error if result else None) or "Google sign-in failed."
            )


# ── App ───────────────────────────────────────────────────────────────────────

class OnboardingApp(App[str | None]):
    CSS = _CSS

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())


def run_onboarding() -> bool:
    """Run the onboarding wizard. Returns True if completed, False if cancelled."""
    return OnboardingApp().run() == "completed"
