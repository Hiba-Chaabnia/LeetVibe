"""LeetVibe TUI — Textual full-screen application."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual.app import App, SystemCommand
from textual.binding import Binding
from textual.command import CommandPalette
from textual.screen import Screen
from textual.system_commands import SystemCommandsProvider
from textual.widget import Widget

from .screens import HomeScreen, ChallengeListScreen, StatsScreen


def _in_maximizable_panel(widget: Widget) -> bool:
    """True if *widget* is inside the code editor or testcase-tabs panel."""
    node: Widget | None = widget
    while node is not None:
        if getattr(node, "id", None) in ("testcase-tabs", "editor-panel"):
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

    CSS_PATH = Path(__file__).parent / "app.tcss"
    TITLE = "LeetVibe"
    SUB_TITLE = "AI Pair Programming for LeetCode"

    # SystemCommandsProvider surfaces get_system_commands() in the palette.
    # Theme and Quit are excluded by overriding get_system_commands() below.
    COMMANDS = frozenset({SystemCommandsProvider})

    SCREENS = {
        "home": HomeScreen,
        "stats": StatsScreen,
    }

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def on_mount(self) -> None:
        self.push_screen("home")

    def action_command_palette(self) -> None:
        """Open the compact palette (no search bar)."""
        if self.use_command_palette and not CommandPalette.is_open(self):
            self.push_screen(_CompactPalette(id="--command-palette"))

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Palette commands: Keys + Maximize (right-panel only). No Theme/Quit/Screenshot."""
        # Keys / help panel toggle
        if screen.query("HelpPanel"):
            yield SystemCommand(
                "Keys",
                "Hide the keys and widget help panel",
                self.action_hide_help_panel,
            )
        else:
            yield SystemCommand(
                "Keys",
                "Show help for the focused widget and a summary of available keys",
                self.action_show_help_panel,
            )

        # Maximize / Minimize — restricted to the code editor and testcase tabs only.
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
