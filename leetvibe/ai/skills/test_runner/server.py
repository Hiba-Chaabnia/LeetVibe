"""MCP skill: test_runner — execute Python code against LeetCode test cases."""


import re
import sys
from pathlib import Path

# Ensure project root is on sys.path when run as a standalone server
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from leetvibe.code_runner import CaseResult, run_tests_with_timeout

mcp = FastMCP("test_runner")


def _count_params(snippet: str) -> int:
    """Count non-self parameters in the first method/function in snippet."""
    m = re.search(r"def \w+\(", snippet)
    if not m:
        return 1
    pos = m.end()
    depth = 1
    params: list[str] = []
    start = pos
    for i in range(pos, len(snippet)):
        ch = snippet[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                params.append(snippet[start:i].strip())
                break
        elif ch == "," and depth == 1:
            params.append(snippet[start:i].strip())
            start = i + 1
    non_self = [p for p in params if p and p.split(":")[0].strip() != "self"]
    return len(non_self) if non_self else 1


def _parse_raw(snippet: str, raw: str) -> list[list[str]]:
    """Group newline-separated raw args into test cases based on param count."""
    n_params = _count_params(snippet)
    lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
    if not lines:
        return []
    cases = []
    for i in range(0, len(lines), n_params):
        chunk = lines[i : i + n_params]
        if chunk:
            cases.append(chunk)
    return cases


def _case_passed(r: CaseResult) -> bool:
    """Comparison result when expected was provided, else "ran without error"."""
    return r.passed if r.passed is not None else not r.error


@mcp.tool()
def run_code(
    code: str,
    snippet: str,
    example_testcases_raw: str = "",
    test_cases: list[dict] = [],
    expected_outputs: list[str] = [],
) -> dict:
    """Execute Python code against test cases. Returns pass/fail per case."""
    if test_cases:
        structured: list[list[str]] = [
            [repr(v) for v in tc.values()] for tc in test_cases
        ]
    elif example_testcases_raw:
        structured = _parse_raw(snippet, example_testcases_raw)
    else:
        structured = []

    # All-or-nothing comparison: bundled test data (e.g. several trees packed
    # into one testCases entry) can ship fewer expected outputs than parsed
    # cases. A partial list would mix "matched expected" and "ran without
    # error" semantics in one result — drop it instead.
    expected = list(expected_outputs or [])
    if expected and len(expected) != len(structured):
        expected = []

    results: list[CaseResult] = run_tests_with_timeout(code, snippet, structured, expected)
    return {
        "cases": [
            {
                "case_num": r.case_num,
                "input": ", ".join(str(arg) for arg in r.inputs),
                "expected": r.expected or "",
                "passed": _case_passed(r),
                "output": repr(r.output),
                "error": r.error or "",
                "stdout": r.stdout or "",
            }
            for r in results
        ],
        "all_passed": all(_case_passed(r) for r in results),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
