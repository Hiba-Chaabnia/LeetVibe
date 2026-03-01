"""HomeScreen — main menu with banner and navigation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from ..widgets.banner import Banner
from ..widgets.status_bar import StatusBar

_GREEN = "#00C44F"


class HomeScreen(Screen):
    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("1", "select_option('learn')", "Learn", show=False),
        Binding("2", "select_option('start')", "Start", show=False),
        Binding("3", "select_option('stats')", "Stats", show=False),
        Binding("4", "select_option('account')", "Account", show=False),
        Binding("5", "quit_app", "Quit", show=False),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="home-scroll"):
            with Container(id="home-content"):
                yield Banner(id="home-banner")
                yield Container(
                    OptionList(
                        Option("📚  Learn     Study a challenge with AI", id="learn"),
                        Option("⚡  Start     Full pair-programming session", id="start"),
                        Option("📊  Stats     Challenge library statistics", id="stats"),
                        Option("🔑  Account   Sign in to sync your progress", id="account"),
                        Option("✖   Quit      Exit LeetVibe", id="quit"),
                        id="main-menu",
                    ),
                    Static("", id="auth-label"),
                    id="home-center",
                )
        yield StatusBar(show_count=False, id="home-status")

    def on_mount(self) -> None:
        self.query_one("#main-menu", OptionList).focus()
        self._refresh_auth()

    def _refresh_auth(self) -> None:
        """Update auth label to reflect current login state."""
        from ...cloud.auth import load_session
        session = load_session()
        label = self.query_one("#auth-label", Static)
        if session:
            email = session.get("email", "")
            label.update(f"[{_GREEN}]● Signed in as {email}[/{_GREEN}]")
        else:
            label.update("[dim]Not signed in — cloud sync disabled[/dim]")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        oid = event.option.id
        if oid == "quit":
            self.app.exit()
        elif oid == "stats":
            self.app.push_screen("stats")
        elif oid == "account":
            self._handle_account()
        else:
            self._go_challenges("learn" if oid == "learn" else "coach")

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_select_option(self, option: str) -> None:
        if option == "quit":
            self.app.exit()
        elif option == "stats":
            self.app.push_screen("stats")
        elif option == "account":
            self._handle_account()
        else:
            self._go_challenges("learn" if option == "learn" else "coach")

    def _handle_account(self) -> None:
        from ...cloud.auth import clear_session, load_session
        session = load_session()
        if session:
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
