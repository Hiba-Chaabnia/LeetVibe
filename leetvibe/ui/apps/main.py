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

    CSS_PATH = Path(__file__).parent / "styles" / "main.tcss"
    TITLE = "LeetVibe"
    SUB_TITLE = "AI Pair Programming for LeetCode"

    # Ctrl+P is freed up for ProblemDetailScreen's "Pair" shortcut. Ctrl+Shift+P
    # (the VS Code convention) collides with Windows Terminal's own built-in
    # command palette, so this uses Ctrl+K instead.
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

    def action_command_palette(self) -> None:
        """Open the compact palette (no search bar)."""
        if self.use_command_palette and not CommandPalette.is_open(self):
            self.push_screen(_CompactPalette(id="--command-palette"))

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Palette commands: Maximize (right-panel only) + Screenshot.

        The "Keys" help-panel command was removed — the footer already covers every
        LeetVibe-specific shortcut, and the panel's remaining content was almost
        entirely generic TextArea/Input editing bindings (cursor movement, cut/copy/
        paste, undo/redo) that don't need a discovery UI.
        """
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

        yield SystemCommand(
            "Screenshot",
            "Save a screenshot of the terminal to SVG",
            self.action_screenshot,
        )
