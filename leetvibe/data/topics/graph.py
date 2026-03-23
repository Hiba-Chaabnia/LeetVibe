from __future__ import annotations

TOPIC: dict = {
    "title": "Graphs",
    "slug": "Graph",
    "recognize": (
        "network traversal, connectivity, cycle detection, \"clone\",\n"
        "  word ladder, friend groups, number of components,\n"
        "  \"bipartite\", \"2-colorable\", \"is it possible to divide into two groups\",\n"
        "  \"walls and gates\", \"rotting oranges\" (multi-source BFS)."
    ),
    "diagram": (
        "  adjacency list:\n"
        "  0: [1, 2]          0 ── 1 ── 3\n"
        "  1: [0, 3]          │\n"
        "  2: [0, 4]          2 ── 4\n"
        "  3: [1]\n"
        "  4: [2]\n"
        "\n"
        "  BFS → queue    shortest path, level order\n"
        "  DFS → stack    connectivity, cycles, components"
    ),
    "when": (
        "Network traversal, connectivity, shortest path (unweighted),\n"
        "  cycle detection, or counting connected components."
    ),
    "pattern": (
        "# BFS — shortest path (unweighted)\n"
        "from collections import deque\n"
        "visited = {start}\n"
        "q = deque([(start, 0)])\n"
        "while q:\n"
        "    node, dist = q.popleft()\n"
        "    if node == target: return dist\n"
        "    for nei in graph[node]:\n"
        "        if nei not in visited:\n"
        "            visited.add(nei)\n"
        "            q.append((nei, dist + 1))\n"
        "\n"
        "# Multi-source BFS — enqueue ALL sources at distance 0 first\n"
        "# Use when: Rotting Oranges, 01 Matrix, Walls and Gates\n"
        "from collections import deque\n"
        "dist = [[float('inf')] * cols for _ in range(rows)]\n"
        "q = deque()\n"
        "for r in range(rows):\n"
        "    for c in range(cols):\n"
        "        if grid[r][c] == SOURCE:     # enqueue ALL sources\n"
        "            dist[r][c] = 0\n"
        "            q.append((r, c))\n"
        "while q:                            # single BFS from all sources\n"
        "    r, c = q.popleft()\n"
        "    for dr, dc in DIRS:\n"
        "        nr, nc = r + dr, c + dc\n"
        "        if 0<=nr<rows and 0<=nc<cols and dist[nr][nc] == float('inf'):\n"
        "            dist[nr][nc] = dist[r][c] + 1\n"
        "            q.append((nr, nc))"
    ),
    "pattern2": (
        "# Bipartite check — 2-colour BFS\n"
        "# A graph is bipartite if it can be coloured with 2 colours s.t.\n"
        "# no two adjacent nodes share the same colour.\n"
        "from collections import deque\n"
        "color = [-1] * n\n"
        "for start in range(n):              # handle disconnected components\n"
        "    if color[start] != -1: continue\n"
        "    color[start] = 0\n"
        "    q = deque([start])\n"
        "    while q:\n"
        "        node = q.popleft()\n"
        "        for nei in graph[node]:\n"
        "            if color[nei] == -1:\n"
        "                color[nei] = 1 - color[node]   # flip colour\n"
        "                q.append(nei)\n"
        "            elif color[nei] == color[node]:    # same colour → not bipartite\n"
        "                return False\n"
        "return True\n"
        "\n"
        "# DFS — connected components + cycle detection (directed)\n"
        "# state: 0=unvisited  1=in-stack  2=done\n"
        "state = [0] * n\n"
        "\n"
        "def dfs(node):\n"
        "    if state[node] == 1: return True   # back edge → cycle\n"
        "    if state[node] == 2: return False\n"
        "    state[node] = 1\n"
        "    for nei in graph[node]:\n"
        "        if dfs(nei): return True\n"
        "    state[node] = 2\n"
        "    return False\n"
        "\n"
        "return any(dfs(i) for i in range(n) if state[i] == 0)"
    ),
    "pitfalls": (
        "• Mark visited BEFORE enqueuing (BFS), not after dequeuing — prevents re-enqueue.\n"
        "• Directed cycle: needs 3 states (unvisited / in-stack / done).\n"
        "• Undirected cycle: track parent to avoid treating the incoming edge as a back edge.\n"
        "• Bipartite: always loop over ALL nodes to handle disconnected components.\n"
        "• Multi-source BFS: enqueue ALL source nodes at distance 0 BEFORE the loop;\n"
        "  never start from one source and then restart — that gives wrong distances.\n"
        "• Python recursion limit: import sys; sys.setrecursionlimit(10**5) before DFS."
    ),
    "time": "O(V + E)",
    "space": "O(V)",
    "problems": [
        ("Clone Graph",                  "M"),
        ("Course Schedule",              "M"),
        ("Number of Islands",            "M"),
        ("Pacific Atlantic Water Flow",  "M"),
        ("Is Graph Bipartite?",          "M"),
        ("Word Ladder",                  "H"),
        ("Rotting Oranges",              "M"),
    ],
    "related": ["Matrix / Grid", "Union Find", "Topological Sort", "Dijkstra", "Bellman-Ford", "Strongly Connected Components", "Eulerian Path / Circuit", "Network Flow"],
}
