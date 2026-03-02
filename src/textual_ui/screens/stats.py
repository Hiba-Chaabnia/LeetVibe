"""StatsScreen — progress, sessions, account and library overview."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static

from ..theme import AMBER, EMBER, FIRE, GOLD, GREEN, LAVA, RED
from ..widgets.status_bar import StatusBar
from .base import BaseScreen


def _bar(count: int, total: int, width: int = 18) -> str:
    """Unicode block progress bar."""
    if total == 0:
        return "░" * width
    filled = round((count / total) * width)
    return "█" * filled + "░" * (width - filled)


def _pct(count: int, total: int) -> str:
    return f"{count / total * 100:.0f}%" if total else "—"


class StatsScreen(BaseScreen):
    """Statistics: progress, sessions, account and library overview."""

    BINDINGS = [
        Binding("escape", "pop_screen", "← Back"),
        Binding("ctrl+q", "quit_app",   "Exit LeetVibe"),
        Binding("q",      "pop_screen", "Back", show=False),
    ]

    DEFAULT_CSS = f"""
    StatsScreen {{
        background: #121212;
    }}
    #stats-scroll {{
        height: 1fr;
        padding: 1 2;
    }}
    .stat-card {{
        padding: 1 2;
        height: auto;
        background: #0e0e0e;
    }}
    #progress-card {{
        border: round {GOLD};
        margin-bottom: 1;
    }}
    #mid-row {{
        height: 9;
        margin-bottom: 1;
    }}
    #sessions-card {{
        border: round {FIRE};
        width: 1fr;
        height: 1fr;
        margin-right: 1;
    }}
    #account-card {{
        border: round {EMBER};
        width: 1fr;
        height: 1fr;
    }}
    #library-card {{
        border: round {LAVA};
        margin-top: 1;
    }}
    #stats-status {{
        background: #121212;
    }}
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="stats-scroll"):
            yield Static(id="progress-card", classes="stat-card")
            with Horizontal(id="mid-row"):
                yield Static(id="sessions-card", classes="stat-card")
                yield Static(id="account-card",  classes="stat-card")
            yield Static(id="library-card", classes="stat-card")
        yield StatusBar(
            hints=[("Esc", "go back", None)],
            id="stats-status",
        )

    def on_mount(self) -> None:
        try:
            from ...config import load_config
            load_config()
        except Exception:
            pass
        self._render_placeholders()
        self._load_stats()

    # ── Placeholders ───────────────────────────────────────────────────

    def _render_placeholders(self) -> None:
        self.query_one("#progress-card", Static).update(
            f"[bold {GOLD}]Your Progress[/bold {GOLD}]\n\n  [dim]Loading…[/dim]"
        )
        self.query_one("#sessions-card", Static).update(
            f"[bold {FIRE}]Sessions[/bold {FIRE}]\n\n  [dim]Loading…[/dim]"
        )
        self.query_one("#account-card", Static).update(
            f"[bold {EMBER}]Account[/bold {EMBER}]\n\n  [dim]Loading…[/dim]"
        )
        self.query_one("#library-card", Static).update(
            f"[bold {LAVA}]Library[/bold {LAVA}]\n\n  [dim]Loading…[/dim]"
        )

    # ── Background loader ──────────────────────────────────────────────

    @work(thread=True)
    def _load_stats(self) -> None:
        from ...challenge_loader import load_all_challenges
        from ...cloud.auth import load_session
        from ...cloud.db import get_session_stats, get_solved_slugs

        challenges   = load_all_challenges()
        easy_total   = sum(1 for c in challenges if c.difficulty == "easy")
        medium_total = sum(1 for c in challenges if c.difficulty == "medium")
        hard_total   = sum(1 for c in challenges if c.difficulty == "hard")
        lib_total    = len(challenges)

        solved        = get_solved_slugs()
        easy_solved   = sum(1 for c in challenges if c.difficulty == "easy"   and c.id in solved)
        medium_solved = sum(1 for c in challenges if c.difficulty == "medium" and c.id in solved)
        hard_solved   = sum(1 for c in challenges if c.difficulty == "hard"   and c.id in solved)
        total_solved  = len(solved)

        session = load_session()
        stats   = get_session_stats() if session else None

        self.app.call_from_thread(
            self._render_all,
            lib_total, easy_total, medium_total, hard_total,
            total_solved, easy_solved, medium_solved, hard_solved,
            session, stats,
        )

    # ── Renderers ──────────────────────────────────────────────────────

    def _render_all(
        self,
        lib_total: int, easy_total: int, medium_total: int, hard_total: int,
        total_solved: int, easy_solved: int, medium_solved: int, hard_solved: int,
        session: dict | None, stats: dict | None,
    ) -> None:
        try:
            self._render_progress(
                lib_total, easy_total, medium_total, hard_total,
                total_solved, easy_solved, medium_solved, hard_solved,
            )
            self._render_sessions(stats)
            self._render_account(session, stats)
            self._render_library(lib_total, easy_total, medium_total, hard_total)
        except Exception:
            pass  # screen may have been unmounted

    def _render_progress(
        self,
        lib_total: int, easy_total: int, medium_total: int, hard_total: int,
        total_solved: int, easy_solved: int, medium_solved: int, hard_solved: int,
    ) -> None:
        text = (
            f"[bold {GOLD}]Your Progress[/bold {GOLD}]\n\n"
            f"  Solved  [bold white]{total_solved:,}[/bold white] / [dim]{lib_total:,}[/dim]  problems\n\n"
            f"  [{GREEN}]●[/{GREEN}] Easy    [{GREEN}]{_bar(easy_solved, easy_total)}  "
            f"{easy_solved:>4} / {easy_total:<4}  {_pct(easy_solved, easy_total):>4}[/{GREEN}]\n"
            f"  [{AMBER}]◆[/{AMBER}] Medium  [{AMBER}]{_bar(medium_solved, medium_total)}  "
            f"{medium_solved:>4} / {medium_total:<4}  {_pct(medium_solved, medium_total):>4}[/{AMBER}]\n"
            f"  [{RED}]★[/{RED}] Hard    [{RED}]{_bar(hard_solved, hard_total)}  "
            f"{hard_solved:>4} / {hard_total:<4}  {_pct(hard_solved, hard_total):>4}[/{RED}]\n"
        )
        self.query_one("#progress-card", Static).update(text)

    def _render_sessions(self, stats: dict | None) -> None:
        count    = stats.get("session_count", 0) if stats else 0
        last     = stats.get("last_updated")      if stats else None
        last_str = last[:10] if last else "—"
        text = (
            f"[bold {FIRE}]Sessions[/bold {FIRE}]\n\n"
            f"  Total   [bold white]{count}[/bold white]\n"
            f"  Last    [bold white]{last_str}[/bold white]\n"
        )
        self.query_one("#sessions-card", Static).update(text)

    def _render_account(self, session: dict | None, stats: dict | None) -> None:
        if not session:
            text = (
                f"[bold {EMBER}]Account[/bold {EMBER}]\n\n"
                f"  Status  [bold #888888]not signed in[/bold #888888]\n"
                f"  [dim]Sign in from the Home screen.[/dim]\n"
            )
        else:
            email    = session.get("email", "—")
            last     = stats.get("last_updated") if stats else None
            sync_str = last[:10] if last else "—"
            text = (
                f"[bold {EMBER}]Account[/bold {EMBER}]\n\n"
                f"  Status  [bold {GREEN}]signed in[/bold {GREEN}]\n"
                f"  Email   [bold white]{email}[/bold white]\n"
                f"  Sync    [bold white]{sync_str}[/bold white]\n"
            )
        self.query_one("#account-card", Static).update(text)

    def _render_library(
        self, total: int, easy: int, medium: int, hard: int
    ) -> None:
        text = (
            f"[bold {LAVA}]Library[/bold {LAVA}]\n\n"
            f"  Total [bold white]{total:,}[/bold white]"
            f"   [{GREEN}]● Easy {easy:,}[/{GREEN}]"
            f"   [{AMBER}]◆ Medium {medium:,}[/{AMBER}]"
            f"   [{RED}]★ Hard {hard:,}[/{RED}]\n"
        )
        self.query_one("#library-card", Static).update(text)
