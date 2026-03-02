"""HomeScreen — main menu with banner and navigation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..theme import DIM, GOLD
from ..widgets.banner import Banner
from ..widgets.status_bar import StatusBar
from .base import BaseScreen

# First column width (chars) — long enough for "Pair Programming"
_COL = 18


def _opt(label: str, desc: str, oid: str) -> Option:
    return Option(f"{label:<{_COL}}{desc}", id=oid)


def _build_options(email: str | None) -> list[Option]:
    if email:
        account_desc = f"Sign out from LeetVibe"
    else:
        account_desc = "Sign in to sync your progress to the cloud"
    return [
        _opt("Learn",            "Let Mistral Vibe teach you the approach, step by step",           "learn"),
        _opt("Pair Programming", "Code alongside Mistral Vibe — live tests, hints, and full feedback", "coach"),
        _opt("Interview",        "Simulate a real technical interview with an AI interviewer",       "interview"),
        _opt("Statistics",       "See how far you've come — sessions, solved problems, and more",   "stats"),
        _opt("Account",          account_desc,                                                       "account"),
        _opt("Quit",             "Exit LeetVibe",                                                    "quit"),
    ]


def _auth_footer(email: str | None) -> str:
    if email:
        return f"[{GOLD}]Signed in with {email}[/{GOLD}]"
    return f"[{DIM}]Not signed in — cloud sync disabled[/{DIM}]"


class HomeScreen(BaseScreen):
    BINDINGS = [
        Binding("ctrl+q", "quit_app", "Quit"),
        Binding("1", "select_option('learn')",     "Learn",     show=False),
        Binding("2", "select_option('coach')",     "Solve",     show=False),
        Binding("3", "select_option('interview')", "Interview", show=False),
        Binding("4", "select_option('stats')",     "Stats",     show=False),
        Binding("5", "select_option('account')",   "Account",   show=False),
        Binding("6", "quit_app",                   "Quit",      show=False),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="home-scroll"):
            with Container(id="home-content"):
                yield Banner(id="home-banner")
                yield Container(
                    OptionList(*_build_options(None), id="main-menu"),
                    id="home-center",
                )
        yield StatusBar(show_count=False, left_label="", id="home-status")

    def on_mount(self) -> None:
        self.query_one("#main-menu", OptionList).focus()
        self._refresh_auth()

    # ── Auth helpers ────────────────────────────────────────────────────

    def _current_email(self) -> str | None:
        from ...cloud.auth import load_session
        session = load_session()
        return session.get("email") if session else None

    def _refresh_auth(self) -> None:
        email = self._current_email()
        # Update footer label
        self.query_one("#home-status", StatusBar).update_left_label(
            _auth_footer(email)
        )
        # Rebuild account option to reflect current sign-in state
        menu = self.query_one("#main-menu", OptionList)
        menu.clear_options()
        for opt in _build_options(email):
            menu.add_option(opt)
        menu.highlighted = 0

    # ── Navigation ──────────────────────────────────────────────────────

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._dispatch(event.option.id)

    def action_select_option(self, option: str) -> None:
        self._dispatch(option)

    def _dispatch(self, oid: str) -> None:
        if oid == "quit":
            self.app.exit()
        elif oid == "stats":
            self.app.push_screen("stats")
        elif oid == "account":
            self._handle_account()
        elif oid in ("learn", "coach", "interview"):
            self._go_challenges(oid)

    def _handle_account(self) -> None:
        from ...cloud.auth import clear_session
        if self._current_email():
            clear_session()
            self._refresh_auth()
            self.notify("Signed out.", severity="information")
        else:
            from .login import LoginScreen
            self.app.push_screen(LoginScreen(), self._on_login_result)

    def _on_login_result(self, result) -> None:
        if result and result.ok:
            self._refresh_auth()
            self.notify(f"Signed in as {result.email}", severity="information")

    def _go_challenges(self, mode: str) -> None:
        from .challenge_list import ChallengeListScreen
        self.app.push_screen(ChallengeListScreen(mode=mode))
