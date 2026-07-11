"""LeetVibe TUI — Textual full-screen application."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual import work
from textual.app import App, SystemCommand
from textual.binding import Binding
from textual.command import CommandPalette
from textual.screen import Screen
from textual.system_commands import SystemCommandsProvider
from textual.widget import Widget

from leetvibe.update_check import check_for_update
from leetvibe.ui.screens.home import HomeScreen
from leetvibe.ui.screens.playbook.screen import PlaybookScreen
from leetvibe.ui.screens.stats import StatsScreen


def _in_maximizable_panel(widget: Widget) -> bool:
    """True if *widget* is inside the code editor or console-tabs panel."""
    node: Widget | None = widget
    while node is not None:
        if getattr(node, "id", None) in ("console-tabs", "editor-panel"):
            return True
        node = node.parent  # type: ignore[assignment]
    return False


class _CompactPalette(CommandPalette):
    """Command palette with the search input hidden (only 2 commands)."""

    DEFAULT_CSS = CommandPalette.DEFAULT_CSS + """
    _CompactPalette #--input {
        display: none;
        height: 0;
    }
    """


class LeetVibeApp(App):
    """LeetVibe full-screen TUI application."""

    CSS_PATH = Path(__file__).parent / "styles" / "main.tcss"
    TITLE = "LeetVibe"
    SUB_TITLE = "AI Pair Programming for LeetCode"

    # Textual's default is ctrl+p, which must stay free for "Pair with AI".
    COMMAND_PALETTE_BINDING = "ctrl+k"

    # SystemCommandsProvider surfaces get_system_commands() in the palette.
    # Theme and Quit are excluded by overriding get_system_commands() below.
    COMMANDS = frozenset({SystemCommandsProvider})

    SCREENS = {
        "home":     HomeScreen,
        "stats":    StatsScreen,
        "concepts": PlaybookScreen,
    }

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def on_mount(self) -> None:
        self.push_screen("home")
        self._notify_if_update_available()
        self._flush_pending_saves()

    @work(thread=True, exclusive=True)
    def _notify_if_update_available(self) -> None:
        latest = check_for_update()
        if latest:
            self.call_from_thread(
                self.notify,
                f"LeetVibe v{latest} is out — run [bold #FF8205]pip install -U leetvibe[/] to upgrade.",
                title="Update available",
                timeout=12,
            )

    @work(thread=True, exclusive=True)
    def _flush_pending_saves(self) -> None:
        """Retry any chat-history saves that failed last run (offline, expired
        token, ...) instead of leaving them stuck unsynced indefinitely."""
        from leetvibe.cloud.auth import is_logged_in
        if not is_logged_in():
            return
        from leetvibe.cloud.db import flush_pending_saves
        synced = flush_pending_saves()
        if synced:
            self.call_from_thread(
                self.notify,
                f"Synced {synced} session{'s' if synced != 1 else ''} that couldn't save earlier.",
                title="Sync recovered",
                timeout=6,
            )

    def action_command_palette(self) -> None:
        """Open the compact palette (no search bar)."""
        if self.use_command_palette and not CommandPalette.is_open(self):
            self.push_screen(_CompactPalette(id="--command-palette"))

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Palette commands: Maximize (right-panel only) + Screenshot."""
        # Maximize / Minimize — restricted to the code editor and console tabs only.
        # Buttons, left-panel content, etc. are intentionally excluded.
        focused = screen.focused
        if screen.maximized is not None:
            yield SystemCommand(
                "Minimize",
                "Minimize the widget and restore to normal size",
                screen.action_minimize,
            )
        elif focused is not None and _in_maximizable_panel(focused):
            yield SystemCommand(
                "Maximize",
                "Maximize the focused widget",
                screen.action_maximize,
            )

        yield SystemCommand(
            "Screenshot",
            "Save a screenshot of the terminal to SVG",
            self.action_screenshot,
        )
