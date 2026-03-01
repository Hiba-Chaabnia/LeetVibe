"""StatsScreen — challenge library statistics and W&B session history."""

from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from ..widgets.status_bar import StatusBar

_FIRE = "#FF8205"
_GREEN = "#00C44F"
_AMBER = "#FFB300"
_RED = "#E53935"


class StatsScreen(Screen):
    """Statistics: challenge library overview and W&B session history."""

    BINDINGS = [
        Binding("escape", "pop_screen", "← Back"),
        Binding("q", "pop_screen", "Back", show=False),
    ]

    DEFAULT_CSS = f"""
    StatsScreen {{
        background: #121212;
    }}
    #stats-header {{
        height: 3;
        background: #1a1a1a;
        border-bottom: solid {_FIRE};
        padding: 0 2;
        content-align: left middle;
        color: {_FIRE};
        text-style: bold;
    }}
    #stats-scroll {{
        height: 1fr;
        padding: 1 2;
    }}
    .stat-card {{
        border: round {_FIRE};
        padding: 1 2;
        margin: 0 0 1 0;
        height: auto;
        background: #0e0e0e;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Static("📊  LeetVibe Statistics", id="stats-header")
        with VerticalScroll(id="stats-scroll"):
            yield Static(id="library-card", classes="stat-card")
            yield Static(id="cloud-card", classes="stat-card")
            yield Static(id="wandb-card", classes="stat-card")
            yield Static(id="skills-card", classes="stat-card")
        yield StatusBar(hints=[("ESC", "Back", None)], id="stats-status")

    def on_mount(self) -> None:
        # Load config to ensure env vars are populated
        try:
            from ...config import load_config
            load_config()
        except Exception:
            pass
        self._render_library()
        self._render_cloud_placeholder()
        self._load_cloud_stats()
        self._render_wandb()
        self._render_skills()

    def _render_library(self) -> None:
        problems_dir = Path(__file__).parent.parent.parent.parent / "problems"
        easy = medium = hard = 0
        if problems_dir.exists():
            for sub, attr in [("easy", "easy"), ("medium", "medium"), ("hard", "hard")]:
                d = problems_dir / sub
                if d.exists():
                    if sub == "easy":
                        easy = sum(1 for _ in d.glob("*.json"))
                    elif sub == "medium":
                        medium = sum(1 for _ in d.glob("*.json"))
                    else:
                        hard = sum(1 for _ in d.glob("*.json"))
        total = easy + medium + hard
        text = (
            f"[bold {_FIRE}]Challenge Library[/bold {_FIRE}]\n\n"
            f"  Total  [bold white]{total:,}[/bold white] problems\n\n"
            f"  [{_GREEN}]●[/{_GREEN}] Easy    [{_GREEN}]{easy:,}[/{_GREEN}]\n"
            f"  [{_AMBER}]◆[/{_AMBER}] Medium  [{_AMBER}]{medium:,}[/{_AMBER}]\n"
            f"  [{_RED}]★[/{_RED}] Hard    [{_RED}]{hard:,}[/{_RED}]\n"
        )
        self.query_one("#library-card", Static).update(text)

    def _render_cloud_placeholder(self) -> None:
        self.query_one("#cloud-card", Static).update(
            f"[bold {_FIRE}]Cloud Sync[/bold {_FIRE}]\n\n  [dim]Loading…[/dim]"
        )

    @work(thread=True)
    def _load_cloud_stats(self) -> None:
        from ...cloud.auth import load_session
        from ...cloud.db import get_session_stats
        session = load_session()
        stats = get_session_stats() if session else None
        self.app.call_from_thread(self._render_cloud, session, stats)

    def _render_cloud(self, session, stats) -> None:
        try:
            card = self.query_one("#cloud-card", Static)
        except Exception:
            return  # screen already unmounted

        if not session:
            text = (
                f"[bold {_FIRE}]Cloud Sync[/bold {_FIRE}]\n\n"
                "  Status: [bold #888888]not signed in[/bold #888888]\n"
                "  [dim]Sign in from the Home screen to sync sessions and chat history.[/dim]\n"
            )
        else:
            email = session.get("email", "")
            count = stats.get("session_count", 0) if stats else 0
            last = stats.get("last_updated") if stats else None
            last_str = last[:10] if last else "—"
            text = (
                f"[bold {_FIRE}]Cloud Sync[/bold {_FIRE}]\n\n"
                f"  Status  :  [bold {_GREEN}]signed in[/bold {_GREEN}]\n"
                f"  Account :  [bold white]{email}[/bold white]\n"
                f"  Sessions:  [bold white]{count}[/bold white]\n"
                f"  Last sync: [bold white]{last_str}[/bold white]\n\n"
                f"  [dim]Chat history and progress are synced automatically.[/dim]\n"
            )
        card.update(text)

    def _render_wandb(self) -> None:
        import os
        api_key = os.environ.get("WANDB_API_KEY", "")
        project = os.environ.get("WANDB_PROJECT", "leetvibe")
        entity = os.environ.get("WANDB_ENTITY", "")

        if api_key:
            text = (
                f"[bold {_FIRE}]Weights & Biases[/bold {_FIRE}]\n\n"
                f"  Status :  [bold {_GREEN}]configured[/bold {_GREEN}]\n"
                f"  Project:  [bold white]{project}[/bold white]\n"
                f"  Entity :  [bold white]{entity or '(default)'}[/bold white]\n\n"
                f"  [dim]Sessions are logged automatically during AI pair-programming.[/dim]\n"
                f"  [dim]Dashboard → wandb.ai/{entity}/{project}[/dim]\n"
            )
        else:
            text = (
                f"[bold {_FIRE}]Weights & Biases[/bold {_FIRE}]\n\n"
                "  Status: [bold #888888]not configured[/bold #888888]\n"
                "  [dim]Add WANDB_API_KEY to .env to enable session tracking.[/dim]\n"
            )
        self.query_one("#wandb-card", Static).update(text)

    def _render_skills(self) -> None:
        skills = [
            ("test_runner", "Execute Python code against test cases"),
            ("voice_narrator", "ElevenLabs TTS — Vibe speaks its reasoning"),
            ("complexity_analyzer", "AST-based time/space complexity analysis"),
            ("teaching_mode", "Structured step-by-step algorithm explanations"),
            ("progress_tracker", "Log learning sessions to Weights & Biases"),
        ]
        lines = [f"[bold {_FIRE}]MCP Skill Servers[/bold {_FIRE}]\n"]
        for name, desc in skills:
            lines.append(f"  [bold white]{name}[/bold white]")
            lines.append(f"  [dim]{desc}[/dim]")
            lines.append("")
        lines.append(f"  [dim]Config: .vibe/config.toml  —  run `vibe` in project root[/dim]")
        self.query_one("#skills-card", Static).update("\n".join(lines))

    def action_pop_screen(self) -> None:
        self.app.pop_screen()
