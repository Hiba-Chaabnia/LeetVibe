from __future__ import annotations

TOPIC: dict = {
    "title": "Floyd-Warshall",
    "slug": "Floyd-Warshall",
    "recognize": (
        "Shortest path between ALL pairs, distance matrix, small graph (n ≤ ~200), negative edges OK.\n"
        "Keywords: find city with smallest reachable neighbours, every pairwise distance."
    ),
    "intuition": (
        "• For each intermediate node k, check if routing through k improves path from i to j.\n"
        "• After the k-th outer iteration, dist[i][j] uses only nodes 0..k as intermediates — all after k=n-1.\n"
        "• k must be the OUTERMOST loop — the recurrence relies on prior k values being already optimal."
    ),
    "diagram": (
        "  Core idea: for each intermediate node k, check if going through k\n"
        "  improves the path from i to j:\n"
        "\n"
        "  dist[i][j] = min(dist[i][j],  dist[i][k] + dist[k][j])\n"
        "\n"
        "  3 nested loops — O(n³):\n"
        "  for k in range(n):          ← intermediate node\n"
        "    for i in range(n):        ← source\n"
        "      for j in range(n):      ← destination\n"
        "        relax (i,j) via k\n"
        "\n"
        "  After: dist[i][i] < 0 → negative cycle exists"
    ),
    "patterns": [
        {
            "name": "Floyd-Warshall All-Pairs Shortest Paths",
            "code": (
                "import math\n"
                "\n"
                "def floyd_warshall(n, edges):\n"
                "    # edges: list of (u, v, weight)\n"
                "    dist = [[math.inf] * n for _ in range(n)]\n"
                "    for i in range(n):\n"
                "        dist[i][i] = 0\n"
                "    for u, v, w in edges:\n"
                "        dist[u][v] = min(dist[u][v], w)   # handle multi-edges\n"
                "\n"
                "    for k in range(n):              # intermediate node\n"
                "        for i in range(n):\n"
                "            for j in range(n):\n"
                "                if dist[i][k] + dist[k][j] < dist[i][j]:\n"
                "                    dist[i][j] = dist[i][k] + dist[k][j]\n"
                "\n"
                "    # Detect negative cycle\n"
                "    if any(dist[i][i] < 0 for i in range(n)):\n"
                "        return None   # negative cycle\n"
                "\n"
                "    return dist   # dist[i][j] = shortest path from i to j"
            ),
        },
        {
            "name": "Find the City With the Smallest Number of Neighbours at Threshold",
            "code": (
                "# After Floyd-Warshall, count reachable cities within distance threshold\n"
                "dist = floyd_warshall(n, edges)\n"
                "\n"
                "best_city  = -1\n"
                "best_count = math.inf\n"
                "for city in range(n):\n"
                "    reachable = sum(\n"
                "        1 for other in range(n)\n"
                "        if other != city and dist[city][other] <= distance_threshold\n"
                "    )\n"
                "    # prefer higher-numbered city on tie\n"
                "    if reachable <= best_count:\n"
                "        best_count = reachable\n"
                "        best_city  = city\n"
                "return best_city"
            ),
        },
    ],
    "variants": (
        "• Standard all-pairs shortest paths — O(n³) time, O(n²) space.\n"
        "• Negative cycle detection — check if any dist[i][i] < 0 after the main loop.\n"
        "• Transitive closure — replace min/+ with OR/AND; dist[i][j] becomes True if j reachable from i.\n"
        "• All-pairs on large graphs — run Dijkstra from each source: O(V·(V+E) log V); better for sparse.\n"
        "• Path reconstruction — maintain next[i][j] matrix; on relaxation set next[i][j]=next[i][k]."
    ),
    "pitfalls": (
        "• k must be the OUTERMOST loop — making it inner breaks the recurrence invariant.\n"
        "• Initialise dist[i][i]=0 and all others to inf BEFORE adding edges.\n"
        "• Multi-edges: use min(dist[u][v], w) when loading — not plain assignment.\n"
        "• Undirected graph: set both dist[u][v] and dist[v][u]."
    ),
    "edge_cases": (
        "• n = 1 — single node; dist[0][0] = 0; triple loop runs once and changes nothing.\n"
        "• No edges — dist[i][j] = inf for all i≠j; all nodes isolated.\n"
        "• Negative cycle — dist[i][i] < 0 after the loop; return None or flag it.\n"
        "• Multi-edges — initialise with min(dist[u][v], w); plain assignment discards cheaper parallel edges."
    ),
    "confusion": (
        "┌───────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                              │\n"
        "├───────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Dijkstra (per source) │ Need distances from ONE source? → Dijkstra O((V+E)   │\n"
        "│                       │ log V).                                              │\n"
        "│                       │ Need ALL pairs? → Floyd-Warshall or run              │\n"
        "│                       │ Dijkstra V times (better for sparse graphs).         │\n"
        "├───────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Bellman-Ford          │ One source with negative edges → Bellman-Ford O(VE). │\n"
        "│                       │ All pairs, small dense graph → Floyd-Warshall O(n³). │\n"
        "└───────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why must k be the outermost loop?\n"
        "• Can you reconstruct the actual shortest path?\n"
        "• The graph has 500 nodes — is Floyd-Warshall feasible?"
    ),
    "time": "O(n³)",
    "space": "O(n²)  for the distance matrix",
    "problems": [
        ("Find the City With Smallest Neighbours", "M"),
        ("Network Delay Time",                     "M"),
        ("Course Schedule IV",                     "M"),
        ("Minimum Cost to Convert String I",       "M"),
        ("Evaluate Division",                      "M"),
    ],
    "related": ["Graphs", "Dijkstra", "Bellman-Ford"],
}
