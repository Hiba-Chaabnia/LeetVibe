"""MCP skill: teaching_mode — structured step-by-step algorithm explanations."""


import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("teaching_mode")

_PATTERNS: dict[str, str] = {
    "two-pointer": "Two pointers move toward each other or in the same direction to avoid O(n²) brute force.",
    "sliding-window": "A window slides over the input, maintaining a running computation in O(n).",
    "binary-search": "Repeatedly halve the search space — O(log n) for sorted arrays.",
    "dp": "Dynamic programming breaks the problem into overlapping subproblems and caches results.",
    "bfs": "BFS explores nodes level by level — optimal for shortest paths in unweighted graphs.",
    "dfs": "DFS explores as deep as possible before backtracking — good for exhaustive search.",
    "hash-map": "Hash maps give O(1) average lookup/insert — trade space for time.",
    "stack": "A stack (LIFO) is key for parentheses matching and monotonic sequence problems.",
    "heap": "A min/max heap gives O(log n) insert and O(1) peek — ideal for top-K and scheduling.",
    "greedy": "Make the locally optimal choice at each step — works when local optimal = global optimal.",
    "backtracking": "Explore all candidates recursively, pruning invalid branches early.",
    "trie": "A prefix tree enables O(m) string search where m is the string length.",
    "union-find": "Track connected components with near-O(1) union and find operations.",
    "monotonic-stack": "Maintain a monotonic stack to find next greater/smaller elements in O(n).",
    "prefix-sum": "Precompute cumulative sums for O(1) range sum queries.",
}


@mcp.tool()
def explain_approach(
    problem_title: str,
    approach: str,
    algorithm_pattern: str,
    code: str = "",
) -> str:
    """Return a structured step-by-step explanation of the algorithm approach.

    approach: "brute_force" | "optimal"
    algorithm_pattern: e.g. "two-pointer", "sliding-window", "dp", "hash-map"
    """
    pattern_key = algorithm_pattern.lower().replace(" ", "-")
    pattern_desc = _PATTERNS.get(pattern_key, f"The {algorithm_pattern} pattern applies here.")
    label = "Brute Force" if approach == "brute_force" else "Optimal Solution"

    lines = [
        f"## {problem_title} — {label}",
        "",
        "**Step 1: Understand the Problem**",
        "Read carefully. Identify: input format, output format, constraints, edge cases.",
        "",
        "**Step 2: Identify the Pattern**",
        f"Pattern: **{algorithm_pattern}**",
        pattern_desc,
        "",
        "**Step 3: Walk Through an Example**",
        "Trace through the first example case manually before writing any code.",
        "",
    ]

    if code:
        lines += [
            "**Step 4: Code Walkthrough**",
            "```python",
            code.strip(),
            "```",
            "",
        ]
    else:
        lines += [
            "**Step 4: Code Walkthrough**",
            f"[Implement the {label.lower()} solution here]",
            "",
        ]

    lines += [
        "**Step 5: Complexity Analysis**",
        "Use the `complexity_analyzer` tool to verify time and space complexity.",
        "",
        "**Step 6: Optimization**",
        (
            "Consider how the chosen pattern can improve over brute force."
            if approach == "brute_force"
            else "This is the optimal solution. Verify with test cases."
        ),
        "",
        f"**Key Insight:** {pattern_desc}",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
