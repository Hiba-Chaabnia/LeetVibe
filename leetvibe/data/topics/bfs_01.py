from __future__ import annotations

TOPIC: dict = {
    "title": "0-1 BFS",
    "slug": "01BFS",
    "recognize": (
        "graph with ONLY edge weights 0 or 1, minimum cost path\n"
        "where moves have cost 0 (free) or 1 (paid),\n"
        "minimum number of obstacles to remove, minimum flips."
    ),
    "diagram": (
        "  Standard BFS: all edges weight 1 → FIFO queue\n"
        "  Dijkstra:     arbitrary weights  → min-heap  O((V+E) log V)\n"
        "  0-1 BFS:      weights 0 or 1     → deque     O(V + E)\n"
        "\n"
        "  Key insight: weight-0 edges don't increase the distance,\n"
        "  so push them to the FRONT of the deque (like a free move).\n"
        "  Weight-1 edges push to the BACK (normal BFS step).\n"
        "\n"
        "  deque: [start]  dist[start]=0\n"
        "  pop left → explore neighbours:\n"
        "    cost=0 → appendleft (same distance level)\n"
        "    cost=1 → append     (next distance level)"
    ),
    "when": (
        "Shortest path in a graph or grid where each edge costs exactly 0 or 1.\n"
        "Faster than Dijkstra (O(V+E) vs O((V+E) log V)).\n"
        "Common disguises: remove obstacles, flip bits, toggle switches."
    ),
    "patterns": [
        {
            "name": "0-1 BFS Template",
            "code": (
                "from collections import deque\n"
                "\n"
                "def zero_one_bfs(grid, sr, sc, er, ec):\n"
                "    rows, cols = len(grid), len(grid[0])\n"
                "    dist = [[float('inf')] * cols for _ in range(rows)]\n"
                "    dist[sr][sc] = 0\n"
                "    dq = deque([(0, sr, sc)])  # (cost, row, col)\n"
                "    DIRS = [(-1,0),(1,0),(0,-1),(0,1)]\n"
                "\n"
                "    while dq:\n"
                "        d, r, c = dq.popleft()\n"
                "        if d > dist[r][c]: continue   # stale entry\n"
                "        for dr, dc in DIRS:\n"
                "            nr, nc = r + dr, c + dc\n"
                "            if not (0 <= nr < rows and 0 <= nc < cols): continue\n"
                "            # cost = 0 if cell is free, 1 if obstacle to remove\n"
                "            w = 1 if grid[nr][nc] == 1 else 0\n"
                "            if dist[r][c] + w < dist[nr][nc]:\n"
                "                dist[nr][nc] = dist[r][c] + w\n"
                "                if w == 0: dq.appendleft((dist[nr][nc], nr, nc))\n"
                "                else:      dq.append((dist[nr][nc], nr, nc))\n"
                "\n"
                "    return dist[er][ec]"
            ),
        },
        {
            "name": "Minimum Cost to Make at Least One Valid Path in a Grid",
            "code": (
                "# Each cell points in a direction; changing it costs 1\n"
                "from collections import deque\n"
                "\n"
                "def min_cost(grid):\n"
                "    rows, cols = len(grid), len(grid[0])\n"
                "    # Direction vectors for grid values 1(right),2(left),3(down),4(up)\n"
                "    DIRS = [(0,1),(0,-1),(1,0),(-1,0)]\n"
                "    dist = [[float('inf')] * cols for _ in range(rows)]\n"
                "    dist[0][0] = 0\n"
                "    dq = deque([(0, 0, 0)])\n"
                "\n"
                "    while dq:\n"
                "        d, r, c = dq.popleft()\n"
                "        if d > dist[r][c]: continue\n"
                "        for i, (dr, dc) in enumerate(DIRS):\n"
                "            nr, nc = r + dr, c + dc\n"
                "            if not (0 <= nr < rows and 0 <= nc < cols): continue\n"
                "            # cost 0 if following existing arrow, 1 if changing it\n"
                "            w = 0 if grid[r][c] == i + 1 else 1\n"
                "            if dist[r][c] + w < dist[nr][nc]:\n"
                "                dist[nr][nc] = dist[r][c] + w\n"
                "                if w == 0: dq.appendleft((dist[nr][nc], nr, nc))\n"
                "                else:      dq.append((dist[nr][nc], nr, nc))\n"
                "\n"
                "    return dist[rows-1][cols-1]"
            ),
        },
    ],
    "pitfalls": (
        "• Still check for stale entries (d > dist[r][c]): continue —\n"
        "  a node can be added to the deque multiple times.\n"
        "• appendleft for cost=0 (free moves go to FRONT);\n"
        "  append for cost=1 (paid moves go to BACK).\n"
        "• 0-1 BFS only works when weights are exactly 0 or 1.\n"
        "  For weights {0, k} for any k, use Dijkstra instead.\n"
        "• The deque maintains the invariant that costs are non-decreasing\n"
        "  front-to-back — this is why 0-1 BFS gives correct shortest paths."
    ),
    "time": "O(V + E)  — each node processed at most twice",
    "space": "O(V)  dist array + deque",
    "problems": [
        ("Minimum Cost to Make Valid Path in Grid",   "H"),
        ("Shortest Path in Binary Matrix",            "M"),
        ("Minimum Obstacle Removal to Reach Corner",  "H"),
        ("Minimum Number of Flips to Make Binary Grid Palindromic", "M"),
        ("K-Similar Strings",                         "H"),
    ],
    "related": ["Graphs", "Dijkstra", "Matrix / Grid", "Queue"],
}
