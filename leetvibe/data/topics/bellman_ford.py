from __future__ import annotations

TOPIC: dict = {
    "title": "Bellman-Ford",
    "slug": "Bellman-Ford",
    "recognize": (
        "shortest path with NEGATIVE edge weights, negative cycle,\n"
        "cheapest flights within K stops, distributed routing."
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
    "when": (
        "Shortest path when edge weights can be negative.\n"
        "Detecting negative cycles. K-step constrained shortest paths."
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
    "pitfalls": (
        "• Always copy dist before each pass when the problem has a hop limit —\n"
        "  otherwise a single pass can chain multiple edges in one iteration.\n"
        "• Early-exit optimisation: if no edge was relaxed, stop early.\n"
        "• Dijkstra fails with negative edges; use Bellman-Ford instead.\n"
        "• Time is O(V × E) — slow for dense graphs with no negative edges;\n"
        "  prefer Dijkstra (O((V+E) log V)) when all weights are non-negative."
    ),
    "time": "O(V × E)",
    "space": "O(V)",
    "problems": [
        ("Cheapest Flights Within K Stops", "M"),
        ("Network Delay Time",              "M"),
        ("Negative Weight Cycle",           "M"),
        ("Minimum Cost to Reach City",      "M"),
        ("Path With Minimum Effort",        "M"),
    ],
    "related": ["Dijkstra", "Graphs", "Dynamic Programming", "Topological Sort"],
}
