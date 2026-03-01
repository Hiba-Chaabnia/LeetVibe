"""Tests for skills/teaching_mode/server.py — structured algorithm explanations."""

from __future__ import annotations

import pytest
from skills.teaching_mode.server import explain_approach, _PATTERNS


# ── header ────────────────────────────────────────────────────────────────────


def test_brute_force_label_in_output():
    result = explain_approach("Two Sum", "brute_force", "hash-map")
    assert "Brute Force" in result


def test_optimal_label_in_output():
    result = explain_approach("Two Sum", "optimal", "hash-map")
    assert "Optimal Solution" in result


def test_problem_title_in_header():
    result = explain_approach("Climbing Stairs", "optimal", "dp")
    assert "Climbing Stairs" in result


# ── steps ─────────────────────────────────────────────────────────────────────


def test_all_six_steps_present():
    result = explain_approach("Foo", "optimal", "two-pointer")
    for step in range(1, 7):
        assert f"Step {step}" in result, f"Missing Step {step}"


def test_step_1_understand():
    result = explain_approach("Foo", "optimal", "bfs")
    assert "Understand" in result or "understand" in result


def test_step_2_pattern_label():
    result = explain_approach("Foo", "optimal", "sliding-window")
    assert "sliding-window" in result or "Sliding-window" in result or "sliding window" in result.lower()


def test_step_5_complexity_mention():
    result = explain_approach("Foo", "optimal", "dp")
    assert "complexity" in result.lower() or "Complexity" in result


# ── pattern descriptions ──────────────────────────────────────────────────────


def test_known_pattern_description_included():
    result = explain_approach("X", "optimal", "hash-map")
    assert "O(1)" in result or "hash" in result.lower()


def test_two_pointer_description():
    result = explain_approach("X", "optimal", "two-pointer")
    assert "pointer" in result.lower() or "O(n²)" in result


def test_binary_search_description():
    result = explain_approach("X", "optimal", "binary-search")
    assert "log" in result.lower() or "halv" in result.lower() or "sorted" in result.lower()


def test_unknown_pattern_fallback():
    result = explain_approach("X", "optimal", "my-custom-pattern")
    assert "my-custom-pattern" in result


# ── code block ────────────────────────────────────────────────────────────────


def test_code_included_when_provided():
    code = "def twoSum(nums, target): pass"
    result = explain_approach("Two Sum", "optimal", "hash-map", code=code)
    assert "twoSum" in result
    assert "```python" in result


def test_code_not_included_when_empty():
    result = explain_approach("Two Sum", "optimal", "hash-map", code="")
    assert "```python" not in result


def test_code_placeholder_present_when_no_code():
    result = explain_approach("Two Sum", "brute_force", "hash-map")
    assert "[" in result  # placeholder like [Implement the brute force solution here]


# ── key insight line ──────────────────────────────────────────────────────────


def test_key_insight_line_present():
    result = explain_approach("X", "optimal", "dp")
    assert "Key Insight" in result


# ── parametrised: all registered patterns render without error ────────────────


@pytest.mark.parametrize("pattern", list(_PATTERNS.keys()))
def test_all_known_patterns_render(pattern):
    result = explain_approach("Problem", "optimal", pattern)
    assert isinstance(result, str)
    assert len(result) > 100
    assert "Step 1" in result
    # Pattern description should appear somewhere
    assert _PATTERNS[pattern][:20] in result


# ── return type ───────────────────────────────────────────────────────────────


def test_returns_string():
    assert isinstance(explain_approach("X", "optimal", "dp"), str)


def test_output_is_markdown_style():
    result = explain_approach("X", "optimal", "dp")
    assert result.startswith("#")  # starts with a markdown heading
