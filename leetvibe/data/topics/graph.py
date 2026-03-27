from __future__ import annotations

TOPIC: dict = {
    "title": "Graphs",
    "slug": "Graph",
    "recognize": (
        "Network traversal, connectivity, cycle detection, clone, bipartite check, word ladder, friend groups.\n"
        "Multi-source BFS: rotting oranges, walls and gates, 01 matrix (nearest source to each cell)."
    ),
    "intuition": (
        "• BFS expands level by level — the first time a node is reached, its distance is provably minimal.\n"
        "• DFS tracks which nodes are on the current call stack — a back edge to an in-stack node proves a cycle.\n"
        "• Multi-source BFS: enqueue ALL sources at distance 0 before the loop; one BFS, not one per source."
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
    "patterns": [
        {
            "name": "BFS — shortest path (unweighted)",
            "code": (
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
                "        if grid[r][c] == SOURCE:\n"
                "            dist[r][c] = 0\n"
                "            q.append((r, c))\n"
                "while q:\n"
                "    r, c = q.popleft()\n"
                "    for dr, dc in DIRS:\n"
                "        nr, nc = r + dr, c + dc\n"
                "        if 0<=nr<rows and 0<=nc<cols and dist[nr][nc] == float('inf'):\n"
                "            dist[nr][nc] = dist[r][c] + 1\n"
                "            q.append((nr, nc))"
            ),
        },
        {
            "name": "Bipartite check — 2-colour BFS",
            "code": (
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
                "                color[nei] = 1 - color[node]\n"
                "                q.append(nei)\n"
                "            elif color[nei] == color[node]:\n"
                "                return False\n"
                "return True\n"
                "\n"
                "# DFS — directed cycle detection\n"
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
        },
    ],
    "variants": (
        "• BFS shortest path (unweighted) — single-source; mark visited on ENQUEUE, not dequeue.\n"
        "• Multi-source BFS — enqueue all sources at distance 0 before the loop.\n"
        "• DFS connectivity / component count — track visited; new DFS per unvisited starting node.\n"
        "• Directed cycle detection — three-state DFS (unvisited / in-stack / done).\n"
        "• Undirected cycle detection — two-state DFS; pass parent to skip the incoming edge.\n"
        "• Bipartite check — 2-colour BFS or DFS; loop over all nodes to handle disconnected components.\n"
        "• Clone graph — DFS/BFS with an old→new node map to avoid infinite loops on cycles.\n"
        "• Word Ladder — words as nodes, single-letter-change as edges; BFS gives minimum steps."
    ),
    "pitfalls": (
        "• Mark visited BEFORE enqueuing — prevents the same node being enqueued multiple times.\n"
        "• Directed cycle: needs 3 states; undirected: track parent to avoid back-edge false positives.\n"
        "• Bipartite: always loop over ALL nodes — disconnected components are silently missed otherwise.\n"
        "• Multi-source BFS: all sources go in BEFORE the while loop — never restart BFS per source.\n"
        "• Python recursion limit: sys.setrecursionlimit(10**5) before deep DFS."
    ),
    "edge_cases": (
        "• Empty graph — BFS returns inf/unreachable; component count is 0; bipartite is True.\n"
        "• Self-loop — directed cycle detected immediately (state[node]==1 on revisit). Undirected: handle separately.\n"
        "• Disconnected graph in bipartite check — outer for-loop over all nodes handles this.\n"
        "• Very deep graph — convert DFS to iterative with an explicit stack, or setrecursionlimit."
    ),
    "confusion": (
        "┌─────────────────────┬─────────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                                 │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────────┤\n"
        "│ Dijkstra            │ All edges unweighted (or weight 1)? → BFS.              │\n"
        "│                     │ Non-negative variable weights? → Dijkstra.              │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────────┤\n"
        "│ Union Find          │ Need shortest path or traversal order? → BFS/DFS.       │\n"
        "│                     │ Just connectivity / component membership? → Union Find. │\n"
        "└─────────────────────┴─────────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• The graph is weighted — what replaces BFS?\n"
        "• Can you detect a cycle in an undirected graph without tracking the parent?\n"
        "• Your DFS is recursive and the graph has 10⁵ nodes — what breaks?"
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
