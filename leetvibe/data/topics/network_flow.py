from __future__ import annotations

TOPIC: dict = {
    "title": "Network Flow",
    "slug": "Network Flow",
    "recognize": (
        "Maximum flow, minimum cut, maximum bipartite matching, minimum path cover.\n"
        "Capacity constraints on edges. 'Maximum number of non-overlapping paths.'\n"
        "Usually disguised — look for assignment problems and bottleneck questions."
    ),
    "intuition": (
        "• Max flow = min cut: the most you can push from S to T equals the smallest\n"
        "  capacity 'bottleneck' separating them. Find it by saturating edges greedily.\n"
        "• Reverse edges let you undo past decisions — sending flow backward cancels\n"
        "  previously committed flow, so the algorithm can correct early mistakes.\n"
        "• Bipartite matching = max flow with unit capacities. König's theorem:\n"
        "  max matching = min vertex cover (bipartite graphs only)."
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
    "variants": (
        "• Edmonds-Karp (BFS augmenting paths) — O(VE²); use for general max flow.\n"
        "• Ford-Fulkerson (DFS) — O(E × max_flow); avoid for large capacities.\n"
        "• Dinic's algorithm — O(V²E), O(E√V) for unit capacities; faster in practice.\n"
        "• Max bipartite matching — unit-capacity max flow or augmenting-path DFS.\n"
        "• Min vertex cover — König's: equals max matching in bipartite graphs.\n"
        "• Min path cover in DAG — n minus max bipartite matching on split-node graph."
    ),
    "pitfalls": (
        "• Always add a reverse edge with 0 capacity — the residual graph needs both directions.\n"
        "• Use BFS (not DFS) for Edmonds-Karp — BFS guarantees O(VE²); DFS can be O(E × max_flow).\n"
        "• Bipartite matching DFS: reset the visited set for each unmatched left node.\n"
        "• Min cut = max flow value — find the cut by BFS in residual from source after termination."
    ),
    "edge_cases": (
        "• No path from S to T — first BFS finds nothing; return 0 immediately.\n"
        "• Source == sink — undefined; guard at call site.\n"
        "• Bipartite duplicate edges — adj list has v multiple times; visited set handles it correctly."
    ),
    "confusion": (
        "┌──────────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with      │ Distinguishing question                               │\n"
        "├──────────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Shortest path (Dijkstra) │ Minimising cost on weighted edges? → Dijkstra.        │\n"
        "│                          │ Maximising throughput through capacity edges? → Flow. │\n"
        "├──────────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Bipartite graph check    │ Just verify bipartite (2-colour)? → BFS/DFS.          │\n"
        "│                          │ Need maximum matching on bipartite graph? → Flow.     │\n"
        "└──────────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why must you add reverse edges with 0 capacity?\n"
        "• How do you find the actual minimum cut (not just its value)?\n"
        "• What is König's theorem and when do you use it?"
    ),
    "time": "O(V × E²) Edmonds-Karp  /  O(V × E) bipartite matching",
    "space": "O(V + E)  residual graph",
    "problems": [
        ("Max Flow / Min Cut",              "H"),
        ("Maximum Bipartite Matching",      "H"),
        ("Minimum Path Cover in DAG",       "H"),
        ("Maximum Number of Accepted Invitations", "M"),
        ("Maximum Students Taking Exam",           "H"),
    ],
    "related": ["Graphs", "Dijkstra", "Union Find"],
}
