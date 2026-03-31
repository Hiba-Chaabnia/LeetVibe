"""GoogleAuthScreen — opens browser and waits for OAuth callback."""

from __future__ import annotations

import asyncio
import webbrowser

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Key
from textual.widgets import Label, Static

from ...widgets import HintLabel
from .base import AuthScreenBase


class GoogleAuthScreen(AuthScreenBase):
    def compose(self) -> ComposeResult:
        with Static(id="form-container"):
            yield Label("Sign in with Google", id="form-title")
            yield Label("", id="form-error")
            with Horizontal(id="form-hint"):
                yield HintLabel("Esc", "cancel", self._cancel)

    def on_mount(self) -> None:
        self._run_google_auth()

    def _cancel(self) -> None:
        self.dismiss(None)

    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            self._cancel()

    @work
    async def _run_google_auth(self) -> None:
        from leetvibe.cloud.auth import GoogleAuthState, start_google_auth

        self._set_status("Opening your browser…")
        state = await asyncio.to_thread(start_google_auth)

        if not isinstance(state, GoogleAuthState):
            self._set_status(state.error or "Google auth failed.")
            return

        webbrowser.open(state.oauth_url)
        self._set_status(
            "Waiting for Google sign-in in your browser…\n"
            "Switch back here once you've signed in."
        )

        completed = await asyncio.to_thread(state.done.wait, 120)

        if not completed:
            self._set_status("Timed out. Press Esc and try again.")
            return

        result = state.result
        if result and result.ok:
            self.dismiss(result)
        else:
            self._set_status((result.error if result else None) or "Google sign-in failed.")

    def _set_status(self, msg: str) -> None:
        try:
            self.query_one("#form-error", Label).update(msg)
        except Exception:
            pass
