"""GoogleAuthScreen (onboarding) — opens browser and waits for OAuth callback."""

from __future__ import annotations

import webbrowser

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static


class GoogleAuthScreen(Screen):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Sign in with Google", id="form-title")
            yield Label("", id="form-error")
            yield Label(
                "[bold #FF8205]Esc[/bold #FF8205] to cancel",
                id="form-hint",
            )

    def on_mount(self) -> None:
        self._run_google_auth()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

    @work
    async def _run_google_auth(self) -> None:
        import asyncio
        from ...cloud.auth import GoogleAuthState, start_google_auth

        self.query_one("#form-error", Label).update("Opening your browser…")
        state = await asyncio.to_thread(start_google_auth)

        if not isinstance(state, GoogleAuthState):
            self.query_one("#form-error", Label).update(state.error or "Google auth failed.")
            return

        webbrowser.open(state.oauth_url)
        self.query_one("#form-error", Label).update(
            "Waiting for Google sign-in in your browser…\n"
            "Switch back here once you've signed in."
        )

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
