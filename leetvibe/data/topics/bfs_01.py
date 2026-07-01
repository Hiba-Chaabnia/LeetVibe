from __future__ import annotations

TOPIC: dict = {
    "title": "0-1 BFS",
    "slug": "01BFS",
    "recognize": (
        "Graph with ONLY edge weights 0 or 1, minimum cost path where moves cost 0 (free) or 1 (paid).\n"
        "Common disguises: remove obstacles, flip bits, toggle switches, minimum flips."
    ),
    "intuition": (
        "• A deque stays sorted by cost: weight-0 edges go to the FRONT (same level), weight-1 to the BACK.\n"
        "• This gives correct shortest paths in O(V+E) — no heap, no log factor.\n"
        "• Only works when weights are exactly 0 or 1; use Dijkstra for any other weights."
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
    "variants": (
        "• Obstacle removal (grid of 0/1) — cost = grid[nr][nc]; classic template above.\n"
        "• Arrow-flip grid — cost = 0 if following existing arrow, else 1.\n"
        "• Minimum flips/toggles — encode state as a node; cost = 1 if flip required, 0 otherwise.\n"
        "• Weights {0, k} for k > 1 — 0-1 BFS does NOT apply; use Dijkstra.\n"
        "• Weights in {0, 1, 2} — split each weight-2 edge into two weight-1 edges via a virtual node."
    ),
    "pitfalls": (
        "• appendleft for cost=0 (free moves go to FRONT); append for cost=1 (paid go to BACK).\n"
        "• Still check stale entries: if d > dist[r][c]: continue.\n"
        "• 0-1 BFS only works for weights exactly 0 or 1 — use Dijkstra for anything else."
    ),
    "edge_cases": (
        "• src == dst — dist[dst] = 0 immediately; return 0 before the loop.\n"
        "• 1×1 grid — single cell is both source and destination; return 0.\n"
        "• All cells are obstacles — answer is shortest grid path length minus 1; dist initialised to inf.\n"
        "• Grid with all cost-0 edges — degenerates to plain BFS; correctness unaffected."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                           │\n"
        "├─────────────────────┼───────────────────────────────────────────────────┤\n"
        "│ Standard BFS        │ Are all edge weights equal (all 1)? → plain BFS.  │\n"
        "│                     │ Weights only 0 or 1? → 0-1 BFS (same O(V+E) but   │\n"
        "│                     │ handles the two-cost structure correctly).        │\n"
        "├─────────────────────┼───────────────────────────────────────────────────┤\n"
        "│ Dijkstra            │ Are weights strictly {0,1}? → 0-1 BFS (faster, no │\n"
        "│                     │ heap).                                            │\n"
        "│                     │ Any other positive weights? → Dijkstra.           │\n"
        "└─────────────────────┴───────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why not just use Dijkstra here?\n"
        "• What if some edges have weight 2 instead of 1?\n"
        "• Can you solve this with standard BFS by modelling the graph differently?"
    ),
    "time": "O(V + E)  — each node processed at most twice",
    "space": "O(V)  dist array + deque",
    "problems": [
        ("Minimum Cost to Make Valid Path in Grid",   "H"),
        ("Minimum Obstacle Removal to Reach Corner",  "H"),
        ("Minimum Sideway Jumps",                     "M"),
        ("Minimum Moves to Move a Box to Target",     "H"),
        ("Shortest Bridge",                           "M"),
    ],
    "related": ["Graphs", "Dijkstra", "Matrix / Grid", "Queue"],
}
