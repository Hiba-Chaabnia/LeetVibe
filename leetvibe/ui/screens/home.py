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


def _build_options(email: str | None, has_key: bool) -> list[Option]:
    if email:
        account_desc = "Sign out from LeetVibe"
    else:
        account_desc = "Sign in to sync your progress to the cloud"

    if has_key:
        solving_opts = [
            _opt("Learn",            "Let LeetVibe teach you the approach, step by step",              "learn"),
            _opt("Pair Programming", "Code alongside LeetVibe — live tests, hints, and full feedback", "pair"),
            _opt("Interview",        "Simulate a real technical interview with an AI interviewer",      "interview"),
        ]
    else:
        solving_opts = [
            _opt("Practice", "Browse, code, and test — no AI, just you and the problem", "practice"),
        ]

    return solving_opts + [
        _opt("Playbook",    "Recognise patterns faster, solve problems smarter",              "concepts"),
        _opt("Statistics",  "See how far you've come — sessions, solved problems, and more",  "stats"),
        _opt("Account",     account_desc,                                                      "account"),
        _opt("AI Settings", "Manage your Mistral and ElevenLabs API keys",                     "ai_settings"),
        _opt("Quit",        "Exit LeetVibe",                                                   "quit"),
    ]


def _auth_footer(email: str | None) -> str:
    if email:
        return f"[{GOLD}]Signed in with {email}[/{GOLD}]"
    return f"[{DIM}]Not signed in — cloud sync disabled[/{DIM}]"


class HomeScreen(BaseScreen):
    # Number keys select by position — the menu's option count and order
    # shift with sign-in state and whether a Mistral key is set, so a fixed
    # id-per-key mapping would go stale; index-based stays correct either way.
    BINDINGS = [
        Binding("ctrl+q", "quit_app", "Quit"),
        Binding("1", "select_index(0)", show=False),
        Binding("2", "select_index(1)", show=False),
        Binding("3", "select_index(2)", show=False),
        Binding("4", "select_index(3)", show=False),
        Binding("5", "select_index(4)", show=False),
        Binding("6", "select_index(5)", show=False),
        Binding("7", "select_index(6)", show=False),
        Binding("8", "select_index(7)", show=False),
    ]

    def compose(self) -> ComposeResult:
        from ...config import has_mistral_key
        with VerticalScroll(id="home-scroll"):
            with Container(id="home-content"):
                yield Banner(id="home-banner")
                yield Container(
                    OptionList(*_build_options(None, has_mistral_key()), id="main-menu"),
                    id="home-center",
                )
        yield StatusBar(
            show_count=False,
            left_label=_auth_footer(None),
            id="home-status",
        )

    def on_mount(self) -> None:
        self.query_one("#main-menu", OptionList).focus()
        self._refresh_menu()
        self.set_timer(0.5, self._refresh_menu)

    def on_screen_resume(self) -> None:
        """Re-check auth and key state — either can change on a pushed screen
        (Account, AI Settings) that we return to this screen from."""
        self._refresh_menu()

    # ── Menu state ──────────────────────────────────────────────────────

    def _current_email(self) -> str | None:
        from ...cloud.auth import load_session
        session = load_session()
        return session.get("email") if session else None

    def _refresh_menu(self) -> None:
        from ...config import has_mistral_key
        email = self._current_email()
        self.query_one("#home-status", StatusBar).update_left_label(
            _auth_footer(email)
        )
        menu = self.query_one("#main-menu", OptionList)
        menu.clear_options()
        for opt in _build_options(email, has_mistral_key()):
            menu.add_option(opt)
        menu.highlighted = 0

    # ── Navigation ──────────────────────────────────────────────────────

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._dispatch(event.option.id)

    def action_select_index(self, index: int) -> None:
        menu = self.query_one("#main-menu", OptionList)
        if 0 <= index < menu.option_count:
            option = menu.get_option_at_index(index)
            self._dispatch(option.id)

    def _dispatch(self, oid: str) -> None:
        if oid == "quit":
            self.app.exit()
        elif oid == "stats":
            self.app.push_screen("stats")
        elif oid == "concepts":
            self.app.push_screen("concepts")
        elif oid == "account":
            self._handle_account()
        elif oid == "ai_settings":
            self._go_ai_settings()
        elif oid in ("learn", "pair", "interview", "practice"):
            self._go_problems(oid)

    def _handle_account(self) -> None:
        if self._current_email():
            from .confirm import ConfirmModal
            self.app.push_screen(
                ConfirmModal(
                    "Sign Out",
                    "Cloud sync will stop until you sign back in.",
                    confirm_label="Sign Out",
                ),
                self._on_sign_out_confirmed,
            )
        else:
            from .auth import AuthChoiceScreen
            self.app.push_screen(AuthChoiceScreen(), self._on_login_result)

    def _on_sign_out_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        from ...cloud.auth import clear_session
        clear_session()
        self._refresh_menu()
        self.notify("Signed out.", severity="information")

    def _on_login_result(self, result) -> None:
        if result and result.ok:
            self._refresh_menu()
            self.notify(f"Signed in as {result.email}", severity="information")

    def _go_problems(self, mode: str) -> None:
        from .problem.list import ProblemListScreen
        self.app.push_screen(ProblemListScreen(mode=mode))

    def _go_ai_settings(self) -> None:
        from ...config import has_mistral_key
        if has_mistral_key():
            # Settings has multiple actions once a key exists — worth its own screen.
            from .ai_settings import AISettingsScreen
            self.app.push_screen(AISettingsScreen())
        else:
            # Nothing to pick between yet — skip straight to adding the key.
            # Esc on that screen pops right back to Home, since Home is what
            # pushed it.
            from .onboarding.api_key import ApiKeyScreen
            self.app.push_screen(ApiKeyScreen(standalone=True), self._on_mistral_saved)

    def _on_mistral_saved(self, saved: bool | None) -> None:
        """First-time add (this path only runs when there was no key yet).
        Offer ElevenLabs right away if it isn't already set, instead of
        leaving the user to find "Add ElevenLabs Voice Key" in AI Settings
        afterward."""
        if not saved:
            return
        self.notify("Mistral API key saved.", severity="information")
        from ...config import has_elevenlabs_key
        if has_elevenlabs_key():
            return
        from .onboarding.elevenlabs_key import ElevenLabsKeyScreen
        self.app.push_screen(ElevenLabsKeyScreen(standalone=True))
