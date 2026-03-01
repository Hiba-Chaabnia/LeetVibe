"""Tests for skills/complexity_analyzer/server.py — AST complexity analysis."""

from __future__ import annotations

import pytest
from skills.complexity_analyzer.server import analyze_complexity


# ── helpers ───────────────────────────────────────────────────────────────────


def _time(code: str) -> str:
    return analyze_complexity(code)["time"]


def _space(code: str) -> str:
    return analyze_complexity(code)["space"]


def _explanation(code: str) -> str:
    return analyze_complexity(code)["explanation"]


# ── time complexity ───────────────────────────────────────────────────────────


def test_constant_time_no_loops():
    code = "def f(a, b):\n    return a + b"
    assert _time(code) == "O(1)"


def test_constant_time_conditional():
    code = "def f(x):\n    if x > 0:\n        return x\n    return -x"
    assert _time(code) == "O(1)"


def test_linear_single_for_loop():
    code = "def f(nums):\n    for x in nums:\n        pass"
    assert _time(code) == "O(n)"


def test_linear_single_while_loop():
    code = "def f(n):\n    i = 0\n    while i < n:\n        i += 1"
    assert _time(code) == "O(n)"


def test_quadratic_two_nested_loops():
    code = "def f(nums):\n    for i in nums:\n        for j in nums:\n            pass"
    assert _time(code) == "O(n²)"


def test_cubic_three_nested_loops():
    code = (
        "def f(a):\n"
        "    for i in a:\n"
        "        for j in a:\n"
        "            for k in a:\n"
        "                pass"
    )
    assert _time(code) == "O(n³)"


def test_sort_only_nlogn():
    code = "def f(nums):\n    return sorted(nums)"
    assert _time(code) == "O(n log n)"


def test_sort_method_nlogn():
    code = "def f(nums):\n    nums.sort()\n    return nums"
    assert _time(code) == "O(n log n)"


def test_loop_with_sort_nlogn():
    code = (
        "def f(nums):\n"
        "    s = sorted(nums)\n"
        "    for x in s:\n"
        "        pass"
    )
    assert _time(code) == "O(n log n)"


def test_memoization_detected_in_explanation():
    code = (
        "from functools import lru_cache\n"
        "@lru_cache(maxsize=None)\n"
        "def f(n):\n"
        "    if n <= 1: return n\n"
        "    return f(n-1) + f(n-2)"
    )
    explanation = _explanation(code)
    assert "emoization" in explanation or "cache" in explanation.lower()


def test_cache_decorator_detected():
    code = (
        "from functools import cache\n"
        "@cache\n"
        "def dp(n):\n"
        "    return n"
    )
    explanation = _explanation(code)
    assert "emoization" in explanation or "cache" in explanation.lower()


# ── space complexity ──────────────────────────────────────────────────────────


def test_constant_space_no_alloc():
    code = "def f(a, b):\n    return a + b"
    assert _space(code) == "O(1)"


def test_linear_space_dict():
    code = "def f(nums):\n    seen = {}\n    for n in nums:\n        seen[n] = True"
    assert _space(code) == "O(n)"


def test_linear_space_list_comp():
    code = "def f(nums):\n    return [x * 2 for x in nums]"
    assert _space(code) == "O(n)"


def test_linear_space_dict_call():
    code = "def f():\n    d = dict()\n    return d"
    assert _space(code) == "O(n)"


def test_linear_space_set():
    code = "def f(nums):\n    return set(nums)"
    assert _space(code) == "O(n)"


# ── result structure ──────────────────────────────────────────────────────────


def test_returns_all_keys():
    result = analyze_complexity("def f(): pass")
    assert "time" in result
    assert "space" in result
    assert "explanation" in result


def test_syntax_error_returns_unknown():
    result = analyze_complexity("def f(: broken syntax !!!")
    assert result["time"] == "unknown"
    assert result["space"] == "unknown"
    assert "Syntax error" in result["explanation"] or "syntax" in result["explanation"].lower()


def test_explanation_is_nonempty_string():
    result = analyze_complexity("def f(nums):\n    return sum(nums)")
    assert isinstance(result["explanation"], str)
    assert len(result["explanation"]) > 0


# ── parametrised complexity ladder ────────────────────────────────────────────


@pytest.mark.parametrize("depth,expected", [
    (1, "O(n)"),
    (2, "O(n²)"),
    (3, "O(n³)"),
])
def test_nested_loop_depth(depth, expected):
    indent = "    "
    lines = ["def f(a):"]
    for i in range(depth):
        lines.append(indent * (i + 1) + f"for _{i} in a:")
    lines.append(indent * (depth + 1) + "pass")
    code = "\n".join(lines)
    assert _time(code) == expected
