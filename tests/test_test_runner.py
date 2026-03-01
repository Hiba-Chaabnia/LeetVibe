"""Tests for skills/test_runner/server.py — Python code execution skill."""

from __future__ import annotations

import pytest
from skills.test_runner.server import run_code


# ── helper snippets ───────────────────────────────────────────────────────────

_TWO_SUM_SNIPPET = (
    "class Solution:\n"
    "    def twoSum(self, nums: List[int], target: int) -> List[int]: "
)
_TWO_SUM_CORRECT = (
    "class Solution:\n"
    "    def twoSum(self, nums, target):\n"
    "        seen = {}\n"
    "        for i, n in enumerate(nums):\n"
    "            if target - n in seen:\n"
    "                return [seen[target - n], i]\n"
    "            seen[n] = i\n"
)
_TWO_SUM_WRONG = (
    "class Solution:\n"
    "    def twoSum(self, nums, target):\n"
    "        return [0, 0]  # always wrong\n"
)
_TWO_SUM_TESTS = "[2,7,11,15]\n9"

_CLIMB_SNIPPET = "class Solution:\n    def climbStairs(self, n: int) -> int: "
_CLIMB_CORRECT = (
    "class Solution:\n"
    "    def climbStairs(self, n):\n"
    "        a, b = 1, 1\n"
    "        for _ in range(n - 1):\n"
    "            a, b = b, a + b\n"
    "        return b\n"
)


# ── result structure ──────────────────────────────────────────────────────────


def test_result_has_required_keys():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert "cases" in result
    assert "all_passed" in result


def test_case_has_required_keys():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    case = result["cases"][0]
    for key in ("case_num", "passed", "output", "error", "stdout"):
        assert key in case, f"missing key: {key}"


# ── correct solution ──────────────────────────────────────────────────────────


def test_correct_solution_all_passed():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["all_passed"] is True


def test_correct_solution_case_passed():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert all(c["passed"] for c in result["cases"])


def test_correct_output_value():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["cases"][0]["output"] == repr([0, 1])


def test_correct_solution_no_error():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["cases"][0]["error"] == ""


# ── wrong answer (no exception, just wrong output) ────────────────────────────


def test_wrong_answer_no_exception_still_passes_in_runner():
    # run_code tracks exceptions, not semantic correctness
    result = run_code(_TWO_SUM_WRONG, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    # No exception thrown → passed=True (wrong answer, but no error)
    assert result["cases"][0]["passed"] is True
    assert result["cases"][0]["error"] == ""


# ── runtime errors ────────────────────────────────────────────────────────────


def test_division_by_zero_captured():
    code = "class Solution:\n    def twoSum(self, nums, target):\n        return 1 / 0\n"
    result = run_code(code, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["all_passed"] is False
    assert result["cases"][0]["passed"] is False
    assert "ZeroDivisionError" in result["cases"][0]["error"]


def test_index_error_captured():
    code = "class Solution:\n    def twoSum(self, nums, target):\n        return nums[999]\n"
    result = run_code(code, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["cases"][0]["passed"] is False
    assert "IndexError" in result["cases"][0]["error"]


def test_type_error_captured():
    code = "class Solution:\n    def twoSum(self, nums, target):\n        return 'string' + 1\n"
    result = run_code(code, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["cases"][0]["passed"] is False
    assert result["cases"][0]["error"] != ""


# ── syntax errors ─────────────────────────────────────────────────────────────


def test_syntax_error_captured():
    code = "def bad syntax !!!"
    result = run_code(code, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    # All cases should fail
    assert result["all_passed"] is False
    for case in result["cases"]:
        assert case["passed"] is False
        assert case["error"] != ""


# ── stdout capture ────────────────────────────────────────────────────────────


def test_stdout_captured():
    code = (
        "class Solution:\n"
        "    def twoSum(self, nums, target):\n"
        "        print('debug:', nums)\n"
        "        return [0, 1]\n"
    )
    result = run_code(code, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert "debug" in result["cases"][0]["stdout"]


def test_stdout_empty_when_no_print():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    assert result["cases"][0]["stdout"] == ""


# ── multiple test cases ───────────────────────────────────────────────────────


def test_multiple_raw_cases():
    # Two separate inputs: n=2 and n=3
    result = run_code(_CLIMB_CORRECT, _CLIMB_SNIPPET, "2\n3")
    assert len(result["cases"]) == 2


def test_multiple_cases_all_pass():
    result = run_code(_CLIMB_CORRECT, _CLIMB_SNIPPET, "2\n3")
    assert result["all_passed"] is True


def test_multiple_cases_correct_outputs():
    result = run_code(_CLIMB_CORRECT, _CLIMB_SNIPPET, "2\n3")
    outputs = [c["output"] for c in result["cases"]]
    assert repr(2) in outputs
    assert repr(3) in outputs


# ── empty / edge cases ────────────────────────────────────────────────────────


def test_empty_test_cases_raw_returns_no_test_case_error():
    # code_runner returns a single case with error="No test cases found."
    # when both raw string and test_cases list are empty
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, "")
    assert len(result["cases"]) == 1
    assert result["cases"][0]["passed"] is False
    assert "No test cases" in result["cases"][0]["error"]


def test_structured_test_cases():
    result = run_code(
        _TWO_SUM_CORRECT,
        _TWO_SUM_SNIPPET,
        test_cases=[{"nums": [3, 2, 4], "target": 6}],
    )
    assert len(result["cases"]) >= 1
    # [1, 2] are the indices for nums=[3,2,4], target=6
    assert result["cases"][0]["passed"] is True


# ── case numbering ────────────────────────────────────────────────────────────


def test_case_numbers_start_at_one():
    result = run_code(_CLIMB_CORRECT, _CLIMB_SNIPPET, "2\n3")
    nums = [c["case_num"] for c in result["cases"]]
    assert nums[0] == 1


def test_output_field_is_repr_string():
    result = run_code(_TWO_SUM_CORRECT, _TWO_SUM_SNIPPET, _TWO_SUM_TESTS)
    # Output should be repr() of the result, e.g. "[0, 1]"
    output = result["cases"][0]["output"]
    assert isinstance(output, str)
    assert output.startswith("[") or output.startswith("(")
