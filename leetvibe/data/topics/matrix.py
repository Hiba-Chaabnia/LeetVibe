from __future__ import annotations

TOPIC: dict = {
    "title": "Matrix / Grid",
    "slug": "Matrix",
    "recognize": (
        "grid, matrix, island, flood fill, neighbors,\n"
        "  shortest path in 2D space, 0/1 matrix, walls and gates,\n"
        "  diagonal, anti-diagonal, spiral traversal."
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
    "when": (
        "Shortest path or flood-fill in a 2D grid.\n"
        "  BFS for shortest path; DFS for area/component counting.\n"
        "  Use (r+c) grouping for diagonal traversal problems."
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
                "# Elements on same diagonal share the same r+c value\n"
                "from collections import defaultdict\n"
                "diagonals = defaultdict(list)\n"
                "for r in range(rows):\n"
                "    for c in range(cols):\n"
                "        diagonals[r + c].append(matrix[r][c])\n"
                "\n"
                "# Flatten: alternate direction each diagonal (Diagonal Traverse)\n"
                "result = []\n"
                "for d in range(rows + cols - 1):\n"
                "    diag = diagonals[d]\n"
                "    result.extend(diag if d % 2 == 0 else diag[::-1])\n"
                "\n"
                "# Anti-diagonal grouping: elements share (r - c) value\n"
                "# Useful for: Longest Increasing Path, Top-Left to Bottom-Right diagonals\n"
                "anti_diags = defaultdict(list)\n"
                "for r in range(rows):\n"
                "    for c in range(cols):\n"
                "        anti_diags[r - c].append(matrix[r][c])"
            ),
        },
    ],
    "pitfalls": (
        "• Bounds check: 0 <= nr < rows AND 0 <= nc < cols (both axes).\n"
        "• Multi-source BFS: enqueue ALL sources at distance 0 before the loop starts.\n"
        "• Mark visited when enqueuing, not when dequeuing.\n"
        "• Diagonal grouping: r+c for top-left→bottom-right diagonals;\n"
        "  r-c for top-right→bottom-left (anti-diagonals)."
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
