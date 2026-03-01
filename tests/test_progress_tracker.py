"""Tests for skills/progress_tracker/server.py — W&B session logging.

wandb is mocked via sys.modules patching so tests run offline without a key.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, call

import pytest

# ── helpers ───────────────────────────────────────────────────────────────────

_SESSION_KWARGS = dict(
    problem_id="1",
    problem_title="Two Sum",
    difficulty="Easy",
    solved=True,
    time_seconds=90,
    approaches_tried=2,
    final_complexity="O(n)",
    hints_used=False,
)


def _mock_wandb(run_id: str = "abc123") -> MagicMock:
    mock = MagicMock()
    mock.init.return_value.id = run_id
    return mock


# ── no API key ────────────────────────────────────────────────────────────────


def test_log_session_no_api_key_skips(monkeypatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    from skills.progress_tracker.server import log_session
    result = log_session(**_SESSION_KWARGS)
    assert "skipped" in result.lower()
    assert "WANDB_API_KEY" in result


# ── success path ──────────────────────────────────────────────────────────────


def test_log_session_returns_run_id(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "test-key")
    mock_wandb = _mock_wandb("run-xyz-789")
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    result = log_session(**_SESSION_KWARGS)
    assert "run-xyz-789" in result
    assert "Logged" in result


def test_log_session_calls_wandb_init(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    monkeypatch.setenv("WANDB_PROJECT", "my-proj")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**_SESSION_KWARGS)
    mock_wandb.init.assert_called_once()
    init_kwargs = mock_wandb.init.call_args[1]
    assert init_kwargs["project"] == "my-proj"


def test_log_session_entity_passed_when_set(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    monkeypatch.setenv("WANDB_ENTITY", "my-team")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**_SESSION_KWARGS)
    init_kwargs = mock_wandb.init.call_args[1]
    assert init_kwargs["entity"] == "my-team"


def test_log_session_entity_none_when_not_set(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    monkeypatch.delenv("WANDB_ENTITY", raising=False)
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**_SESSION_KWARGS)
    init_kwargs = mock_wandb.init.call_args[1]
    assert init_kwargs["entity"] is None


def test_log_session_logs_correct_metrics(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**_SESSION_KWARGS)
    mock_wandb.log.assert_called_once()
    logged = mock_wandb.log.call_args[0][0]
    assert logged["solved"] == 1
    assert logged["time_seconds"] == 90
    assert logged["approaches_tried"] == 2
    assert logged["hints_used"] == 0
    assert logged["final_complexity"] == "O(n)"


def test_log_session_unsolved_logs_zero(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    kwargs = dict(_SESSION_KWARGS, solved=False)
    log_session(**kwargs)
    logged = mock_wandb.log.call_args[0][0]
    assert logged["solved"] == 0


def test_log_session_calls_finish(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**_SESSION_KWARGS)
    mock_wandb.finish.assert_called_once()


def test_log_session_tags_include_difficulty(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**_SESSION_KWARGS)
    init_kwargs = mock_wandb.init.call_args[1]
    assert "easy" in init_kwargs["tags"]
    assert "leetvibe" in init_kwargs["tags"]


# ── error handling ────────────────────────────────────────────────────────────


def test_log_session_wandb_error_returns_error_string(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    mock_wandb = MagicMock()
    mock_wandb.init.side_effect = RuntimeError("W&B server unreachable")
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    result = log_session(**_SESSION_KWARGS)
    assert "error" in result.lower()
    assert "W&B server unreachable" in result


def test_log_session_hints_used_bool_to_int(monkeypatch):
    monkeypatch.setenv("WANDB_API_KEY", "k")
    mock_wandb = _mock_wandb()
    monkeypatch.setitem(sys.modules, "wandb", mock_wandb)

    from skills.progress_tracker.server import log_session
    log_session(**dict(_SESSION_KWARGS, hints_used=True))
    logged = mock_wandb.log.call_args[0][0]
    assert logged["hints_used"] == 1
