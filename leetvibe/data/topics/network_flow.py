from __future__ import annotations

TOPIC: dict = {
    "title": "Network Flow",
    "slug": "Network Flow",
    "recognize": (
        "maximum flow, minimum cut, maximum bipartite matching,\n"
        "minimum path cover, capacity constraints on edges,\n"
        "maximum number of non-overlapping paths."
    ),
    "diagram": (
        "  Flow network: source S, sink T, capacities on directed edges\n"
        "\n"
        "  S ──4──► A ──3──► T\n"
        "  │         ▲       ▲\n"
        "  2         2       1\n"
        "  ▼         │       │\n"
        "  B ──3──►  C ──1──►┘\n"
        "\n"
        "  Max flow = min cut (Ford-Fulkerson / max-flow min-cut theorem)\n"
        "  Find augmenting paths (BFS = Edmonds-Karp) until none remain\n"
        "\n"
        "  Bipartite Matching = max flow with unit capacities on all edges"
    ),
    "when": (
        "Problems with explicit capacity/resource constraints between nodes.\n"
        "Maximum bipartite matching (job assignment, interval scheduling).\n"
        "Minimum vertex/edge cover. Rarely appears directly — usually disguised."
    ),
    "patterns": [
        {
            "name": "Edmonds-Karp (BFS-based Ford-Fulkerson) — O(V × E²)",
            "code": (
                "from collections import deque, defaultdict\n"
                "\n"
                "def max_flow(graph, source, sink):\n"
                "    # graph[u][v] = remaining capacity of edge u→v\n"
                "    # Use defaultdict so reverse edges start at 0\n"
                "    flow = 0\n"
                "\n"
                "    while True:\n"
                "        # BFS to find augmenting path\n"
                "        parent = {source: None}\n"
                "        q = deque([source])\n"
                "        while q and sink not in parent:\n"
                "            u = q.popleft()\n"
                "            for v in graph[u]:\n"
                "                if v not in parent and graph[u][v] > 0:\n"
                "                    parent[v] = u\n"
                "                    q.append(v)\n"
                "\n"
                "        if sink not in parent: break  # no augmenting path\n"
                "\n"
                "        # Find bottleneck capacity along the path\n"
                "        path_flow = float('inf')\n"
                "        v = sink\n"
                "        while v != source:\n"
                "            u = parent[v]\n"
                "            path_flow = min(path_flow, graph[u][v])\n"
                "            v = u\n"
                "\n"
                "        # Update residual capacities\n"
                "        v = sink\n"
                "        while v != source:\n"
                "            u = parent[v]\n"
                "            graph[u][v] -= path_flow\n"
                "            graph[v][u] += path_flow   # reverse edge\n"
                "            v = u\n"
                "\n"
                "        flow += path_flow\n"
                "    return flow"
            ),
        },
        {
            "name": "Maximum Bipartite Matching — reduce to max flow",
            "code": (
                "# Or use simpler augmenting-path DFS directly\n"
                "def max_bipartite_matching(n_left, n_right, edges):\n"
                "    # match_left[i] = which right node i is matched to (-1 = unmatched)\n"
                "    match_left  = [-1] * n_left\n"
                "    match_right = [-1] * n_right\n"
                "    adj = [[] for _ in range(n_left)]\n"
                "    for u, v in edges:\n"
                "        adj[u].append(v)\n"
                "\n"
                "    def dfs(u, visited):\n"
                "        for v in adj[u]:\n"
                "            if v in visited: continue\n"
                "            visited.add(v)\n"
                "            if match_right[v] == -1 or dfs(match_right[v], visited):\n"
                "                match_left[u]  = v\n"
                "                match_right[v] = u\n"
                "                return True\n"
                "        return False\n"
                "\n"
                "    matching = 0\n"
                "    for u in range(n_left):\n"
                "        if match_left[u] == -1:\n"
                "            if dfs(u, set()): matching += 1\n"
                "    return matching"
            ),
        },
    ],
    "pitfalls": (
        "• Always add a REVERSE edge with 0 capacity for every forward edge;\n"
        "  the residual graph requires both directions.\n"
        "• Edmonds-Karp uses BFS (not DFS) for augmenting paths — BFS guarantees\n"
        "  O(VE²) complexity; DFS (basic Ford-Fulkerson) can be O(E × max_flow).\n"
        "• Bipartite matching DFS: reset visited set for each unmatched left node —\n"
        "  don't reuse the visited set across different starting nodes.\n"
        "• Max-flow min-cut: the minimum cut equals the maximum flow (duality theorem)."
    ),
    "time": "O(V × E²) Edmonds-Karp  /  O(V × E) bipartite matching",
    "space": "O(V + E)  residual graph",
    "problems": [
        ("Max Flow / Min Cut",              "H"),
        ("Maximum Bipartite Matching",      "H"),
        ("Minimum Path Cover in DAG",       "H"),
        ("Swim in Rising Water",            "H"),
        ("Escape the Spreading Fire",       "H"),
    ],
    "related": ["Graphs", "Dijkstra", "Union Find"],
}
