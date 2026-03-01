"""HomeScreen — main menu with banner and navigation."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..widgets.banner import Banner
from ..widgets.status_bar import StatusBar


class HomeScreen(Screen):
    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("1", "select_option('learn')", "Learn", show=False),
        Binding("2", "select_option('start')", "Start", show=False),
        Binding("3", "select_option('stats')", "Stats", show=False),
        Binding("4", "quit_app", "Quit", show=False),
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
                        Option("✖   Quit      Exit LeetVibe", id="quit"),
                        id="main-menu",
                    ),
                    id="home-center",
                )
        yield StatusBar(show_count=False, id="home-status")

    def on_mount(self) -> None:
        self.query_one("#main-menu", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        oid = event.option.id
        if oid == "quit":
            self.app.exit()
        elif oid == "stats":
            self.app.push_screen("stats")
        else:
            self._go_challenges("learn" if oid == "learn" else "coach")

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_select_option(self, option: str) -> None:
        if option == "quit":
            self.app.exit()
        elif option == "stats":
            self.app.push_screen("stats")
        else:
            self._go_challenges("learn" if option == "learn" else "coach")

    def _go_challenges(self, mode: str) -> None:
        from .challenge_list import ChallengeListScreen
        self.app.push_screen(ChallengeListScreen(mode=mode))
