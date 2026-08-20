"""AISettingsScreen — add, replace, or remove the Mistral and ElevenLabs keys."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from ..widgets import StatusBar
from .base import BaseScreen

_COL = 30


def _opt(label: str, desc: str, oid: str) -> Option:
    return Option(f"{label:<{_COL}}{desc}", id=oid)


def _build_options(has_mistral: bool, has_eleven: bool) -> list[Option]:
    if not has_mistral:
        return [
            _opt("Add Mistral API Key", "Unlocks Learn, Pair Programming and Interview", "mistral_add"),
        ]
    options = [
        _opt("Replace Mistral API Key", "Enter a new key, overwriting the current one",   "mistral_replace"),
        _opt("Remove Mistral API Key",  "Disables AI modes — Practice mode still works",  "mistral_remove"),
    ]
    if has_eleven:
        options += [
            _opt("Replace ElevenLabs Voice Key", "Enter a new key, overwriting the current one", "eleven_replace"),
            _opt("Remove ElevenLabs Voice Key",  "Disables voice narration",                      "eleven_remove"),
        ]
    else:
        options.append(
            _opt("Add ElevenLabs Voice Key", "Optional — enables voice narration", "eleven_add"),
        )
    return options


class AISettingsScreen(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("ctrl+q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        from ...config import has_elevenlabs_key, has_mistral_key
        with VerticalScroll(id="settings-scroll"):
            with Container(id="settings-content"):
                yield Container(
                    OptionList(
                        *_build_options(has_mistral_key(), has_elevenlabs_key()),
                        id="settings-menu",
                    ),
                    id="settings-center",
                )
        yield StatusBar(
            hints=[
                ("Esc", "go back", self.action_pop_screen),
                ("Ctrl+Q", "exit LeetVibe", self.action_quit_app),
            ],
            show_count=False,
            id="settings-status",
        )

    def on_mount(self) -> None:
        self.query_one("#settings-menu", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._dispatch(event.option.id)

    def _dispatch(self, oid: str) -> None:
        if oid in ("mistral_add", "mistral_replace"):
            from .onboarding.api_key import ApiKeyScreen
            # Chain straight into ElevenLabs only when this is a first-time add
            # (no key -> key) — a replace means the user already made their
            # ElevenLabs call earlier, so don't re-ask on every rekey.
            replacing = oid == "mistral_replace"
            on_saved = self._on_mistral_saved if replacing else self._on_mistral_added
            self.app.push_screen(ApiKeyScreen(standalone=True, replacing=replacing), on_saved)
        elif oid == "mistral_remove":
            from .confirm import ConfirmModal
            self.app.push_screen(
                ConfirmModal(
                    "Remove Mistral API Key",
                    "AI modes (Learn, Pair Programming, Interview) will stop working. "
                    "Practice mode is unaffected.",
                    confirm_label="Remove",
                ),
                self._on_mistral_removed,
            )
        elif oid in ("eleven_add", "eleven_replace"):
            from .onboarding.elevenlabs_key import ElevenLabsKeyScreen
            replacing = oid == "eleven_replace"
            self.app.push_screen(
                ElevenLabsKeyScreen(standalone=True, replacing=replacing), self._on_eleven_saved
            )
        elif oid == "eleven_remove":
            from .confirm import ConfirmModal
            self.app.push_screen(
                ConfirmModal(
                    "Remove ElevenLabs Voice Key",
                    "Voice narration will be disabled.",
                    confirm_label="Remove",
                ),
                self._on_eleven_removed,
            )

    def _on_mistral_saved(self, saved: bool | None) -> None:
        if saved:
            self.notify("Mistral API key saved.", severity="information")
        self._refresh()

    def _on_mistral_added(self, saved: bool | None) -> None:
        """Callback for a first-time add (not a replace) — offers ElevenLabs
        right away if it isn't already configured, instead of leaving the
        user to notice and pick it as a separate menu item afterward."""
        if not saved:
            self._refresh()
            return
        self.notify("Mistral API key saved.", severity="information")
        from ...config import has_elevenlabs_key
        if has_elevenlabs_key():
            self._refresh()
            return
        from .onboarding.elevenlabs_key import ElevenLabsKeyScreen
        self.app.push_screen(ElevenLabsKeyScreen(standalone=True), self._on_eleven_saved)

    def _on_mistral_removed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        from ...config import remove_mistral_key
        remove_mistral_key()
        self.notify("Mistral API key removed.", severity="information")
        self._refresh()

    def _on_eleven_saved(self, saved: bool | None) -> None:
        if saved:
            self.notify("ElevenLabs API key saved.", severity="information")
        self._refresh()

    def _on_eleven_removed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        from ...config import remove_elevenlabs_key
        remove_elevenlabs_key()
        self.notify("ElevenLabs API key removed.", severity="information")
        self._refresh()

    def _refresh(self) -> None:
        from ...config import has_elevenlabs_key, has_mistral_key
        menu = self.query_one("#settings-menu", OptionList)
        menu.clear_options()
        for opt in _build_options(has_mistral_key(), has_elevenlabs_key()):
            menu.add_option(opt)
        if menu.option_count:
            menu.highlighted = 0
