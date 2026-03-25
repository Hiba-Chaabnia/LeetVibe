from __future__ import annotations

TOPIC: dict = {
    "title": "Floyd-Warshall",
    "slug": "Floyd-Warshall",
    "recognize": (
        "shortest path between ALL pairs of nodes, distance matrix,\n"
        "find city with smallest number of reachable neighbours,\n"
        "small graph (n ≤ ~200), negative edges OK (but no negative cycles)."
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
    "when": (
        "All-pairs shortest paths on a small dense graph (n ≤ ~200).\n"
        "When you need every pairwise distance, not just from one source.\n"
        "For large graphs, run Dijkstra from each node instead."
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
    "pitfalls": (
        "• Loop order matters: k must be the OUTERMOST loop, not innermost.\n"
        "• Initialise dist[i][i] = 0 and all others to inf BEFORE adding edges.\n"
        "• Multi-edges: use min(dist[u][v], w) when loading edges, not plain assignment.\n"
        "• Only feasible for n ≤ ~200 — O(n³) blows up for large graphs.\n"
        "• Undirected graph: set both dist[u][v] and dist[v][u]."
    ),
    "time": "O(n³)",
    "space": "O(n²)  for the distance matrix",
    "problems": [
        ("Find the City With Smallest Neighbours", "M"),
        ("Network Delay Time",                     "M"),
        ("Cheapest Flights Within K Stops",        "M"),
        ("Evaluate Division",                      "M"),
    ],
    "related": ["Graphs", "Dijkstra", "Bellman-Ford"],
}
