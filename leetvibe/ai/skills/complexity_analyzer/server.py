"""MCP skill: complexity_analyzer — AST-based time/space complexity analysis."""


import ast
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
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


def _scan_tree(tree: ast.AST) -> tuple[bool, bool, bool, bool]:
    """Single AST walk collecting has_sort, has_memo, has_any_iter, has_dynamic_alloc."""
    has_sort = False
    has_memo = False
    has_any_iter = False
    has_dynamic_alloc = False
    _iter_nodes = (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp)
    _alloc_names = frozenset(("dict", "list", "set", "defaultdict", "Counter"))
    for node in ast.walk(tree):
        if isinstance(node, _iter_nodes):
            has_any_iter = True
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
                has_dynamic_alloc = True
        elif isinstance(node, ast.Dict):
            has_dynamic_alloc = True
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ("sort", "sorted"):
                    has_sort = True
            elif isinstance(func, ast.Name):
                if func.id in ("sorted", "sort"):
                    has_sort = True
                if func.id in _alloc_names:
                    has_dynamic_alloc = True
        elif isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else repr(dec)
                if any(kw in dec_str.lower() for kw in ("cache", "lru", "memo")):
                    has_memo = True
    return has_sort, has_memo, has_any_iter, has_dynamic_alloc


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
    has_sort, has_memo, has_any_iter, has_dynamic_alloc = _scan_tree(tree)

    # ── Time complexity heuristic ──────────────────────────────────────
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
    if has_dynamic_alloc:
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
