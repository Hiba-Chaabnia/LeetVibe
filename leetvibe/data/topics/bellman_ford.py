from __future__ import annotations

TOPIC: dict = {
    "title": "Bellman-Ford",
    "slug": "Bellman-Ford",
    "recognize": (
        "Shortest path with NEGATIVE edge weights, negative cycle detection,\n"
        "cheapest flights within K stops, distributed routing with negative costs."
    ),
    "intuition": (
        "• After k passes, dist[v] holds the shortest path using at most k edges — run V-1 passes for all simple paths.\n"
        "• Unlike Dijkstra, no greedy settlement is made, so a later negative edge can correct earlier estimates.\n"
        "• A V-th pass that still relaxes an edge proves a negative cycle exists."
    ),
    "diagram": (
        "  Relax ALL edges (V-1) times:\n"
        "\n"
        "  Graph:  A ──(1)── B ──(-3)── C\n"
        "                    ↑\n"
        "                   (4)\n"
        "                    ↑\n"
        "                    A\n"
        "\n"
        "  dist from A: [0, ∞, ∞]\n"
        "  pass 1 → relax A→B: dist[B]=1; relax B→C: dist[C]=-2\n"
        "  pass 2 → no update\n"
        "  final:  [0, 1, -2]\n"
        "\n"
        "  V-th pass still relaxes → negative cycle detected!"
    ),
    "patterns": [
        {
            "name": "Standard Bellman-Ford",
            "code": (
                "dist = [float('inf')] * n\n"
                "dist[src] = 0\n"
                "\n"
                "for _ in range(n - 1):          # relax all edges n-1 times\n"
                "    updated = False\n"
                "    for u, v, w in edges:        # edges: (from, to, weight)\n"
                "        if dist[u] != float('inf') and dist[u] + w < dist[v]:\n"
                "            dist[v] = dist[u] + w\n"
                "            updated = True\n"
                "    if not updated: break        # early exit if stable\n"
                "\n"
                "# Check for negative cycle (one more pass still relaxes)\n"
                "for u, v, w in edges:\n"
                "    if dist[u] + w < dist[v]:\n"
                "        return None             # negative cycle exists\n"
                "return dist"
            ),
        },
        {
            "name": "Cheapest Flights Within K Stops",
            "code": (
                "# Key: copy dist from previous iteration so each pass\n"
                "# represents exactly ONE additional hop.\n"
                "import math\n"
                "dist = [math.inf] * n\n"
                "dist[src] = 0\n"
                "\n"
                "for _ in range(k + 1):           # k stops = k+1 edges\n"
                "    temp = dist[:]               # snapshot — don't use updates\n"
                "    for u, v, w in flights:\n"
                "        if dist[u] != math.inf and dist[u] + w < temp[v]:\n"
                "            temp[v] = dist[u] + w\n"
                "    dist = temp\n"
                "\n"
                "return dist[dst] if dist[dst] != math.inf else -1"
            ),
        },
    ],
    "variants": (
        "• Standard shortest path — run V-1 passes; add a V-th to detect negative cycles.\n"
        "• K-hop constrained (Cheapest Flights Within K Stops) — run k+1 passes; snapshot dist before each.\n"
        "• Negative cycle detection only — run V-1 passes, then one more; flag if any edge still relaxes.\n"
        "• All-pairs with negatives — run Bellman-Ford from every source: O(V²×E).\n"
        "• SPFA — queue-based variant; only enqueue when distance improves; faster average case."
    ),
    "pitfalls": (
        "• K-stops: snapshot dist before each pass (temp = dist[:]) — chains form within one pass without it.\n"
        "• Early-exit: if no edge was relaxed, stop — don't loop the full V-1 rounds needlessly.\n"
        "• Dijkstra fails with negative edges; use Bellman-Ford."
    ),
    "edge_cases": (
        "• src == dst — dist[dst] = 0 immediately; return 0 without entering the loop.\n"
        "• Unreachable destination — dist[dst] remains inf; return -1 or inf as required.\n"
        "• Negative cycle NOT on the path to dst — dist[dst] is still valid; naively flagging all is wrong.\n"
        "• k == 0 in K-stops — loop runs once (range(1)); only direct src→dst edges considered."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Dijkstra            │ Are all edge weights non-negative? → Dijkstra        │\n"
        "│                     │ (O((V+E) log V)).                                    │\n"
        "│                     │ Any negative weight possible, or need cycle          │\n"
        "│                     │ detection? → Bellman-Ford.                           │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Floyd-Warshall      │ Need shortest path from ONE source, or ALL pairs?    │\n"
        "│                     │ One source → Bellman-Ford.                           │\n"
        "│                     │ All pairs (small V, dense graph) → Floyd-Warshall    │\n"
        "│                     │ (O(V³) but simpler code).                            │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Dijkstra is faster — when would you actually choose Bellman-Ford?\n"
        "• Your solution is O(VE). The graph has 10⁴ nodes and 10⁶ edges — is that acceptable?\n"
        "• What if there's a negative cycle but you still want the shortest path to nodes not affected by it?"
    ),
    "time": "O(V × E)",
    "space": "O(V)",
    "problems": [
        ("Cheapest Flights Within K Stops", "M"),
        ("Network Delay Time",              "M"),
        ("Negative Weight Cycle",           "M"),
        ("Minimum Cost to Reach City",      "M"),
    ],
    "related": ["Dijkstra", "Graphs", "Dynamic Programming", "Topological Sort"],
}
