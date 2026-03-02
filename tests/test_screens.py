"""Tests for AgentSessionScreen and StatsScreen using Textual's test framework.

Uses @pytest.mark.anyio (anyio is pre-installed).
- AgentSessionScreen: _run_agent worker is patched to prevent vibe_agent import.
- StatsScreen: on_mount uses async push_screen.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.textual_ui.screens.agent_session import AgentSessionScreen
from src.textual_ui.screens.stats import StatsScreen


# ── minimal host apps ─────────────────────────────────────────────────────────


def _agent_app(challenge, mode: str = "learn"):
    from textual.app import App

    class AgentApp(App):
        async def on_mount(self) -> None:
            await self.push_screen(AgentSessionScreen(challenge, mode=mode, user_code=""))

    return AgentApp()


def _stats_app():
    from textual.app import App

    class StatsApp(App):
        async def on_mount(self) -> None:
            await self.push_screen(StatsScreen())

    return StatsApp()


# ── AgentSessionScreen ────────────────────────────────────────────────────────
# Worker is always patched so vibe_agent (needs mistralai) is never imported.


@pytest.mark.anyio
async def test_agent_session_mounts_without_crash(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum).run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            # If we reach here the screen mounted without exception


@pytest.mark.anyio
async def test_agent_session_shows_challenge_title(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum).run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            from textual.widgets import Static
            title = pilot.app.screen.query_one("#session-title", Static)
            assert "Two Sum" in str(title.content)


@pytest.mark.anyio
async def test_agent_session_back_button_pops_screen(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        app = _agent_app(two_sum)
        async with app.run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            await pilot.click("#btn-back")
            await pilot.pause(0.1)
            assert not any(isinstance(s, AgentSessionScreen) for s in app.screen_stack)


@pytest.mark.anyio
async def test_agent_session_stop_button_disables_itself(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum).run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            await pilot.click("#btn-stop")
            await pilot.pause(0.1)
            from textual.widgets import Button
            assert pilot.app.screen.query_one("#btn-stop", Button).disabled


@pytest.mark.anyio
async def test_agent_session_learn_mode_active_class(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum, mode="learn").run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            from textual.widgets import Button
            assert "active" in pilot.app.screen.query_one("#btn-learn", Button).classes


@pytest.mark.anyio
async def test_agent_session_coach_mode_active_class(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum, mode="coach").run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            from textual.widgets import Button
            assert "active" in pilot.app.screen.query_one("#btn-coach", Button).classes


@pytest.mark.anyio
async def test_agent_session_escape_pops_screen(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        app = _agent_app(two_sum)
        async with app.run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            await pilot.press("escape")
            await pilot.pause(0.1)
            assert not any(isinstance(s, AgentSessionScreen) for s in app.screen_stack)


@pytest.mark.anyio
async def test_agent_session_mode_buttons_both_exist(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum).run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            from textual.widgets import Button
            assert pilot.app.screen.query_one("#btn-learn", Button) is not None
            assert pilot.app.screen.query_one("#btn-coach", Button) is not None


@pytest.mark.anyio
async def test_agent_session_richlog_exists(two_sum):
    with patch.object(AgentSessionScreen, "_run_agent"):
        async with _agent_app(two_sum).run_test(headless=True) as pilot:
            await pilot.pause(0.1)
            from textual.widgets import RichLog
            assert pilot.app.screen.query_one("#agent-log", RichLog) is not None


# ── StatsScreen ───────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_stats_screen_mounts_without_crash():
    async with _stats_app().run_test(headless=True) as pilot:
        await pilot.pause(0.2)


@pytest.mark.anyio
async def test_stats_screen_library_card_has_content():
    async with _stats_app().run_test(headless=True) as pilot:
        await pilot.pause(0.2)
        from textual.widgets import Static
        rendered = str(pilot.app.screen.query_one("#library-card", Static).content)
        assert any(kw in rendered for kw in ("Total", "Easy", "problem", "Challenge", "Library"))


@pytest.mark.anyio
async def test_stats_screen_shows_skills_card():
    async with _stats_app().run_test(headless=True) as pilot:
        await pilot.pause(0.2)
        from textual.widgets import Static
        rendered = str(pilot.app.screen.query_one("#skills-card", Static).content)
        assert "test_runner" in rendered
        assert "voice_narrator" in rendered


@pytest.mark.anyio
async def test_stats_screen_escape_pops():
    app = _stats_app()
    async with app.run_test(headless=True) as pilot:
        await pilot.pause(0.1)
        await pilot.press("escape")
        await pilot.pause(0.1)
        assert not any(isinstance(s, StatsScreen) for s in app.screen_stack)
