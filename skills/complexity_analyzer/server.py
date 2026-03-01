"""MCP skill: complexity_analyzer — AST-based time/space complexity analysis."""


import ast
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("complexity_analyzer")


def _max_loop_depth(tree: ast.AST) -> int:
    """Return the maximum nesting depth of for/while loops in the tree."""
    max_depth = [0]

    def _walk(node: ast.AST, depth: int) -> None:
        if isinstance(node, (ast.For, ast.While)):
            depth += 1
            max_depth[0] = max(max_depth[0], depth)
        for child in ast.iter_child_nodes(node):
            _walk(child, depth)

    _walk(tree, 0)
    return max_depth[0]


def _has_sort_call(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(
                getattr(func, "attr", None), "__str__", lambda: None
            )()
            if name in ("sorted", "sort"):
                return True
            if isinstance(func, ast.Attribute) and func.attr in ("sort", "sorted"):
                return True
    return False


def _has_memoization(tree: ast.AST) -> bool:
    """Detect @lru_cache / @cache decorators or manual memo dict patterns."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else repr(dec)
                if any(kw in dec_str.lower() for kw in ("cache", "lru", "memo")):
                    return True
    return False


def _has_dynamic_alloc(tree: ast.AST) -> bool:
    """Check for dict/list/set allocations that scale with input."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp)):
            return True
        if isinstance(node, ast.Call):
            func_name = getattr(getattr(node, "func", None), "id", "")
            if func_name in ("dict", "list", "set", "defaultdict", "Counter"):
                return True
    return False


@mcp.tool()
def analyze_complexity(code: str, function_name: str = "") -> dict:
    """Analyze time and space complexity of Python code via AST inspection.

    Returns: {time: "O(n)", space: "O(1)", explanation: "..."}
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"time": "unknown", "space": "unknown", "explanation": f"Syntax error: {exc}"}

    depth = _max_loop_depth(tree)
    has_sort = _has_sort_call(tree)
    has_memo = _has_memoization(tree)

    # ── Time complexity heuristic ──────────────────────────────────────
    has_any_iter = any(
        isinstance(n, (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp))
        for n in ast.walk(tree)
    )

    if depth == 0 and not has_sort and not has_any_iter:
        time_c = "O(1)"
        time_note = "No loops or sorting detected."
    elif depth <= 1 and has_sort and not has_any_iter:
        time_c = "O(n log n)"
        time_note = "Sorting dominates."
    elif depth == 1 and has_sort:
        time_c = "O(n log n)"
        time_note = "Single loop + sorting."
    elif depth == 0 or depth == 1:
        time_c = "O(n)"
        time_note = "Single-level iteration."
    elif depth == 2:
        time_c = "O(n²)"
        time_note = "Two nested loops."
    elif depth == 3:
        time_c = "O(n³)"
        time_note = "Three nested loops."
    else:
        time_c = f"O(n^{depth})"
        time_note = f"{depth} nested loops."

    if has_memo:
        time_note += " Memoization detected — effective complexity may be lower."

    # ── Space complexity heuristic ─────────────────────────────────────
    if _has_dynamic_alloc(tree):
        space_c = "O(n)"
        space_note = "Dynamic data structures (dict/list/set) scale with input."
    else:
        space_c = "O(1)"
        space_note = "No dynamic allocations detected."

    return {
        "time": time_c,
        "space": space_c,
        "explanation": f"Time: {time_note}  Space: {space_note}",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
