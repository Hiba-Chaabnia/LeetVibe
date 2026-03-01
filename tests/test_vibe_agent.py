"""Tests for src/vibe_agent.py — VibeAgent Mistral streaming loop.

Mistral's client.chat.stream() is mocked so no real API calls are made.
Skipped automatically if mistralai is not installed.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

# Skip the entire module if mistralai is not installed in this environment
pytest.importorskip("mistralai", reason="mistralai not installed — run: pip install mistralai")

from src.vibe_agent import VibeAgent, SYSTEM_PROMPT, _TOOLS


# ── mock helpers ──────────────────────────────────────────────────────────────


def _text_event(content: str, finish_reason: str | None = None) -> MagicMock:
    """A streaming event that contains text content."""
    event = MagicMock()
    choice = MagicMock()
    choice.delta.content = content
    choice.delta.tool_calls = []
    choice.finish_reason = finish_reason
    event.data.choices = [choice]
    return event


def _tool_event(idx: int, tc_id: str, name: str, arguments: str) -> MagicMock:
    """A streaming event that contains a (fragment of a) tool call."""
    event = MagicMock()
    choice = MagicMock()
    choice.delta.content = None
    tc = MagicMock()
    tc.index = idx
    tc.id = tc_id
    tc.function = MagicMock()
    tc.function.name = name
    tc.function.arguments = arguments
    choice.delta.tool_calls = [tc]
    choice.finish_reason = None
    event.data.choices = [choice]
    return event


class _StreamCtx:
    """A context manager that yields a pre-defined list of events."""

    def __init__(self, events: list) -> None:
        self._events = events

    def __enter__(self):
        return iter(self._events)

    def __exit__(self, *_):
        pass


def _make_agent(dummy_config) -> VibeAgent:
    with patch("src.vibe_agent.Mistral"):
        return VibeAgent(dummy_config)


# ── tool schema ───────────────────────────────────────────────────────────────


def test_tools_list_has_five_entries():
    assert len(_TOOLS) == 5


def test_tools_all_have_function_type():
    for tool in _TOOLS:
        assert tool["type"] == "function"


def test_tools_names():
    names = {t["function"]["name"] for t in _TOOLS}
    assert names == {"run_code", "narrate", "analyze_complexity", "explain_approach", "log_session"}


def test_run_code_required_params():
    run_code_tool = next(t for t in _TOOLS if t["function"]["name"] == "run_code")
    assert "code" in run_code_tool["function"]["parameters"]["required"]
    assert "snippet" in run_code_tool["function"]["parameters"]["required"]


# ── system prompt ─────────────────────────────────────────────────────────────


def test_system_prompt_is_nonempty():
    assert len(SYSTEM_PROMPT) > 100


def test_system_prompt_mentions_workflow():
    assert "run_code" in SYSTEM_PROMPT
    assert "narrate" in SYSTEM_PROMPT or "narrat" in SYSTEM_PROMPT.lower()


# ── _build_prompt ─────────────────────────────────────────────────────────────


def test_build_prompt_includes_title(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    prompt = agent._build_prompt(two_sum, "learn", "")
    assert "Two Sum" in prompt


def test_build_prompt_includes_difficulty(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    prompt = agent._build_prompt(two_sum, "learn", "")
    assert "Easy" in prompt


def test_build_prompt_includes_snippet(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    prompt = agent._build_prompt(two_sum, "learn", "")
    assert "twoSum" in prompt


def test_build_prompt_includes_test_cases(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    prompt = agent._build_prompt(two_sum, "learn", "")
    assert "[2,7,11,15]" in prompt


def test_build_prompt_learn_mode_no_user_code_section(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    prompt = agent._build_prompt(two_sum, "learn", "")
    assert "User's Attempt" not in prompt


def test_build_prompt_coach_mode_includes_user_code(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    user_code = "def twoSum(): return [0, 1]"
    prompt = agent._build_prompt(two_sum, "coach", user_code)
    assert "User's Attempt" in prompt
    assert user_code in prompt


def test_build_prompt_coach_mode_empty_code_no_section(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    prompt = agent._build_prompt(two_sum, "coach", "")
    assert "User's Attempt" not in prompt


# ── _execute_tool ─────────────────────────────────────────────────────────────


def test_execute_tool_run_code(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    with patch("skills.test_runner.server.run_code", return_value={"all_passed": True, "cases": []}) as mock_fn:
        result = agent._execute_tool("run_code", {"code": "x", "snippet": "y"})
    mock_fn.assert_called_once_with(code="x", snippet="y")
    assert result["all_passed"] is True


def test_execute_tool_analyze_complexity(dummy_config):
    agent = _make_agent(dummy_config)
    with patch("skills.complexity_analyzer.server.analyze_complexity", return_value={"time": "O(n)"}) as mock_fn:
        result = agent._execute_tool("analyze_complexity", {"code": "def f(): pass"})
    mock_fn.assert_called_once_with(code="def f(): pass")
    assert result["time"] == "O(n)"


def test_execute_tool_narrate(dummy_config):
    agent = _make_agent(dummy_config)
    with patch("skills.voice_narrator.server.narrate", return_value="playing 1.0s") as mock_fn:
        result = agent._execute_tool("narrate", {"text": "hello"})
    mock_fn.assert_called_once_with(text="hello")
    assert "playing" in result


def test_execute_tool_explain_approach(dummy_config):
    agent = _make_agent(dummy_config)
    with patch("skills.teaching_mode.server.explain_approach", return_value="## Two Sum") as mock_fn:
        result = agent._execute_tool("explain_approach", {"problem_title": "Two Sum", "approach": "optimal", "algorithm_pattern": "hash-map"})
    assert result == "## Two Sum"


def test_execute_tool_log_session(dummy_config):
    agent = _make_agent(dummy_config)
    with patch("skills.progress_tracker.server.log_session", return_value="Logged to W&B run abc") as mock_fn:
        result = agent._execute_tool("log_session", {"problem_id": "1", "problem_title": "Two Sum", "difficulty": "Easy", "solved": True, "time_seconds": 60, "approaches_tried": 1, "final_complexity": "O(n)", "hints_used": False})
    assert "Logged" in result


def test_execute_tool_unknown_returns_error(dummy_config):
    agent = _make_agent(dummy_config)
    result = agent._execute_tool("nonexistent_tool", {})
    assert "error" in result
    assert "nonexistent_tool" in str(result)


# ── solve_streaming — text only ───────────────────────────────────────────────


def test_solve_streaming_yields_text_chunks(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    events = [
        _text_event("Let me think about this."),
        _text_event(" I'll use a hash map."),
    ]
    agent.client.chat.stream.return_value = _StreamCtx(events)

    chunks = list(agent.solve_streaming(two_sum, mode="learn"))
    text = "".join(c for c in chunks if not c.startswith("\n[dim]"))
    assert "Let me think about this." in text
    assert "hash map" in text


def test_solve_streaming_ends_with_session_complete(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    agent.client.chat.stream.return_value = _StreamCtx([_text_event("Done.")])

    chunks = list(agent.solve_streaming(two_sum))
    full = "".join(chunks)
    assert "Session complete" in full


def test_solve_streaming_stops_when_no_tool_calls(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    call_count = 0

    def fake_stream(**_kwargs):
        nonlocal call_count
        call_count += 1
        return _StreamCtx([_text_event("hello")])

    agent.client.chat.stream.side_effect = fake_stream
    list(agent.solve_streaming(two_sum))
    # Should only call the API once (no tool calls → break)
    assert call_count == 1


# ── solve_streaming — tool call ───────────────────────────────────────────────


def test_solve_streaming_executes_tool_call(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    args = json.dumps({"code": "class Solution:\n    def twoSum(self, n, t): return [0,1]", "snippet": "class Solution:\n    def twoSum(self, nums, target): "})

    # First stream: one tool call
    first_events = [
        _tool_event(0, "tc-1", "run_code", args),
    ]
    # Second stream: text only (agent finishes)
    second_events = [_text_event("All tests passed!")]

    call_count = 0

    def fake_stream(**_kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _StreamCtx(first_events)
        return _StreamCtx(second_events)

    agent.client.chat.stream.side_effect = fake_stream

    with patch.object(agent, "_execute_tool", return_value={"all_passed": True, "cases": []}) as mock_exec:
        chunks = list(agent.solve_streaming(two_sum))

    mock_exec.assert_called_once()
    assert mock_exec.call_args[0][0] == "run_code"


def test_solve_streaming_tool_result_in_output(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    args = json.dumps({"code": "x", "snippet": "y"})
    first_events = [_tool_event(0, "tc-1", "run_code", args)]
    second_events = [_text_event("Done.")]

    call_count = 0

    def fake_stream(**_kwargs):
        nonlocal call_count
        call_count += 1
        return _StreamCtx(first_events if call_count == 1 else second_events)

    agent.client.chat.stream.side_effect = fake_stream

    with patch.object(agent, "_execute_tool", return_value={"all_passed": True}):
        chunks = list(agent.solve_streaming(two_sum))

    full = "".join(chunks)
    assert "run_code" in full  # tool name shown in output


# ── solve_streaming — API error ───────────────────────────────────────────────


def test_solve_streaming_api_exception_yields_error(dummy_config, two_sum):
    agent = _make_agent(dummy_config)

    class _BrokenCtx:
        def __enter__(self):
            raise ConnectionError("API timeout")

        def __exit__(self, *_):
            pass

    agent.client.chat.stream.return_value = _BrokenCtx()
    chunks = list(agent.solve_streaming(two_sum))
    full = "".join(chunks)
    assert "error" in full.lower() or "Error" in full


# ── solve_streaming — max turns safety cap ────────────────────────────────────


def test_solve_streaming_respects_max_turns(dummy_config, two_sum):
    agent = _make_agent(dummy_config)
    args = json.dumps({"code": "x", "snippet": "y"})

    # Always return a tool call → would loop forever without cap
    def always_tool(**_kwargs):
        return _StreamCtx([_tool_event(0, "tc", "run_code", args)])

    agent.client.chat.stream.side_effect = always_tool

    with patch.object(agent, "_execute_tool", return_value={"all_passed": False}):
        chunks = list(agent.solve_streaming(two_sum))

    # Should terminate; total API calls ≤ 20
    assert agent.client.chat.stream.call_count <= 20
    full = "".join(chunks)
    assert "Session complete" in full
