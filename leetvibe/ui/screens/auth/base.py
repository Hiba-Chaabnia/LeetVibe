"""Shared base for the auth flow screens.

Every screen in the flow ends by calling ``self.dismiss(result)`` — an
``AuthResult`` on success, ``None`` on skip/cancel. The caller decides what
that means: onboarding exits the setup app, the Account menu refreshes Home.
"""

from __future__ import annotations

from pathlib import Path

from textual.screen import Screen


class AuthScreenBase(Screen):
    CSS_PATH = Path(__file__).parent / "auth.tcss"
