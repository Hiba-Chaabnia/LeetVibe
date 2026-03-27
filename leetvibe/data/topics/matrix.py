from __future__ import annotations

TOPIC: dict = {
    "title": "Matrix / Grid",
    "slug": "Matrix",
    "recognize": (
        "Grid traversal, number of islands, flood fill, shortest path in 2D, spiral, diagonal, word search.\n"
        "Signal: 2D input where cells are nodes and edges connect adjacent neighbours."
    ),
    "intuition": (
        "• A grid IS a graph — BFS/DFS apply directly; DIRS = [(-1,0),(1,0),(0,-1),(0,1)] encodes the edges.\n"
        "• BFS: mark visited on ENQUEUE, not dequeue — prevents the same cell being added twice.\n"
        "• Multi-source BFS: enqueue ALL sources at distance 0 before the loop — one BFS, not one per source."
    ),
    "diagram": (
        "  4-directional neighbours of (r, c):\n"
        "  DIRS = [(-1,0),(1,0),(0,-1),(0,1)]\n"
        "\n"
        "         (r-1,c)\n"
        "            ↑\n"
        "  (r,c-1) ← (r,c) → (r,c+1)\n"
        "            ↓\n"
        "         (r+1,c)\n"
        "\n"
        "  Diagonal groups: r+c is constant along each diagonal\n"
        "  Anti-diagonal:   r-c is constant  (top-right to bottom-left)\n"
        "\n"
        "  Multi-source BFS — enqueue ALL sources at distance 0 first."
    ),
    "patterns": [
        {
            "name": "BFS shortest path in grid",
            "code": (
                "from collections import deque\n"
                "DIRS = [(-1,0),(1,0),(0,-1),(0,1)]\n"
                "rows, cols = len(grid), len(grid[0])\n"
                "visited = {(sr, sc)}\n"
                "q = deque([(sr, sc, 0)])\n"
                "while q:\n"
                "    r, c, dist = q.popleft()\n"
                "    if (r, c) == (er, ec): return dist\n"
                "    for dr, dc in DIRS:\n"
                "        nr, nc = r + dr, c + dc\n"
                "        if (0 <= nr < rows and 0 <= nc < cols\n"
                "                and (nr, nc) not in visited\n"
                "                and grid[nr][nc] != WALL):\n"
                "            visited.add((nr, nc))\n"
                "            q.append((nr, nc, dist + 1))"
            ),
        },
        {
            "name": "DFS island area — mark visited in-place",
            "code": (
                "def dfs(r, c):\n"
                "    if r < 0 or r >= rows or c < 0 or c >= cols: return 0\n"
                "    if grid[r][c] != '1': return 0\n"
                "    grid[r][c] = '0'   # mark visited\n"
                "    return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)\n"
                "\n"
                "count = 0\n"
                "for r in range(rows):\n"
                "    for c in range(cols):\n"
                "        if grid[r][c] == '1':\n"
                "            dfs(r, c)\n"
                "            count += 1\n"
                "\n"
                "# Diagonal Traversal — group by (r + c)\n"
                "from collections import defaultdict\n"
                "diagonals = defaultdict(list)\n"
                "for r in range(rows):\n"
                "    for c in range(cols):\n"
                "        diagonals[r + c].append(matrix[r][c])\n"
                "\n"
                "result = []\n"
                "for d in range(rows + cols - 1):\n"
                "    diag = diagonals[d]   # collected top-down (increasing r)\n"
                "    # even diagonals travel UP-RIGHT → reverse the top-down order\n"
                "    result.extend(diag[::-1] if d % 2 == 0 else diag)\n"
                "\n"
                "# Anti-diagonal grouping: r - c constant\n"
                "anti_diags = defaultdict(list)\n"
                "for r in range(rows):\n"
                "    for c in range(cols):\n"
                "        anti_diags[r - c].append(matrix[r][c])"
            ),
        },
    ],
    "variants": (
        "• BFS shortest path — single source; mark visited on enqueue; O(m×n).\n"
        "• Multi-source BFS — all sources at distance 0 before the loop (01 Matrix, Rotting Oranges, Walls and Gates).\n"
        "• DFS flood fill / island count — mark in-place to avoid a visited set; restore if grid must be unchanged.\n"
        "• 8-directional grid — add diagonal pairs (±1,±1) to DIRS.\n"
        "• Spiral traversal — maintain four boundaries (top, bottom, left, right); shrink after each direction.\n"
        "• Diagonal grouping — r+c for top-left→bottom-right; r-c for anti-diagonals.\n"
        "• Word Search — DFS with in-place marking; restore on backtrack."
    ),
    "pitfalls": (
        "• Bounds check: 0 <= nr < rows AND 0 <= nc < cols — use the correct dimension for each axis.\n"
        "• Mark visited on ENQUEUE, not dequeue — prevents the same cell being added multiple times.\n"
        "• Multi-source BFS: enqueue ALL sources at distance 0 before the while loop.\n"
        "• Diagonal: r+c for top-left→bottom-right; r-c for anti-diagonals (easy to mix up)."
    ),
    "edge_cases": (
        "• 1×1 grid — single cell; BFS returns 0 if src==dst; DFS island count = 1 if '1', else 0.\n"
        "• All cells walls — BFS exhausts queue without reaching target; return -1 or inf.\n"
        "• Non-square grid (m ≠ n) — bounds check must use rows for row axis and cols for col axis.\n"
        "• Very large grid DFS — recursion depth can hit Python's limit; convert to iterative DFS or setrecursionlimit."
    ),
    "confusion": (
        "┌───────────────────────┬────────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                            │\n"
        "├───────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ General graph BFS/DFS │ Is the structure a 2D grid with (r,c) coordinates? │\n"
        "│                       │ → Matrix pattern (DIRS, bounds check). Adjacency   │\n"
        "│                       │ list? → General graph traversal.                   │\n"
        "├───────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Sliding Window        │ Moving a rectangular subgrid window? → 2D Sliding  │\n"
        "│                       │ Window. Exploring reachable cells? → BFS/DFS.      │\n"
        "└───────────────────────┴────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you solve Number of Islands without modifying the grid?\n"
        "• What if moves are 8-directional (including diagonals)?\n"
        "• Your DFS crashes on a 10⁶-cell grid — how do you fix it?"
    ),
    "time": "O(m × n)",
    "space": "O(m × n)  visited set  /  O(m×n) recursion stack for DFS",
    "problems": [
        ("Number of Islands",            "M"),
        ("Flood Fill",                   "E"),
        ("Rotting Oranges",              "M"),
        ("01 Matrix",                    "M"),
        ("Pacific Atlantic Water Flow",  "M"),
        ("Word Search",                  "M"),
        ("Diagonal Traverse",            "M"),
        ("Spiral Matrix",               "M"),
        ("Set Matrix Zeroes",            "M"),
        ("Surrounded Regions",           "M"),
    ],
    "related": ["Graphs", "Union Find"],
}
