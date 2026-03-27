from __future__ import annotations

TOPIC: dict = {
    "title": "Dijkstra",
    "slug": "Dijkstra",
    "recognize": (
        "Shortest path, minimum cost, weighted graph, non-negative edge weights.\n"
        "Keywords: network delay, cheapest flights, minimum effort — any weighted shortest path with no negative edges."
    ),
    "intuition": (
        "• Greedily settle the node with the smallest known distance first — it can never be improved later.\n"
        "• Non-negative weights guarantee the first time a node is popped, its distance is already optimal.\n"
        "• Negative edges break this: a later edge could improve a settled node, so use Bellman-Ford instead."
    ),
    "diagram": (
        "  Weighted graph  (src = 0):\n"
        "  0 ──4── 1\n"
        "  │       │\n"
        "  2       2\n"
        "  │       │\n"
        "  2 ──1── 3\n"
        "\n"
        "  dist: [0, ∞, ∞, ∞]  heap: [(0,0)]\n"
        "  pop (0,0) → relax: dist[1]=4, dist[2]=2\n"
        "  pop (2,2) → relax: dist[3]=3\n"
        "  pop (3,3) → relax: dist[1]=min(4,5) — no update\n"
        "  pop (4,1) → done\n"
        "  dist: [0, 4, 2, 3]"
    ),
    "patterns": [
        {
            "name": "Dijkstra's Algorithm",
            "code": (
                "import heapq\n"
                "\n"
                "def dijkstra(graph, src, n):\n"
                "    # graph[u] = [(weight, v), ...]\n"
                "    dist = [float('inf')] * n\n"
                "    dist[src] = 0\n"
                "    heap = [(0, src)]         # (distance, node)\n"
                "    while heap:\n"
                "        d, u = heapq.heappop(heap)\n"
                "        if d > dist[u]: continue   # stale entry — skip\n"
                "        for w, v in graph[u]:\n"
                "            if dist[u] + w < dist[v]:\n"
                "                dist[v] = dist[u] + w\n"
                "                heapq.heappush(heap, (dist[v], v))\n"
                "    return dist"
            ),
        },
        {
            "name": "Dijkstra with path reconstruction",
            "code": (
                "import heapq\n"
                "\n"
                "dist = [float('inf')] * n\n"
                "prev = [-1] * n               # predecessor array\n"
                "dist[src] = 0\n"
                "heap = [(0, src)]\n"
                "\n"
                "while heap:\n"
                "    d, u = heapq.heappop(heap)\n"
                "    if d > dist[u]: continue\n"
                "    for w, v in graph[u]:\n"
                "        if dist[u] + w < dist[v]:\n"
                "            dist[v] = dist[u] + w\n"
                "            prev[v] = u\n"
                "            heapq.heappush(heap, (dist[v], v))\n"
                "\n"
                "# Reconstruct path from src to dst\n"
                "path, node = [], dst\n"
                "while node != -1:\n"
                "    path.append(node)\n"
                "    node = prev[node]\n"
                "path.reverse()                 # path is built backwards\n"
                "return path if path[0] == src else []   # [] if dst unreachable"
            ),
        },
    ],
    "variants": (
        "• Standard single-source — returns dist[] from src to all nodes.\n"
        "• Path reconstruction — add prev[] array; walk back from dst to src and reverse.\n"
        "• Early termination — break as soon as dst is popped; skips rest of the graph.\n"
        "• Grid Dijkstra — nodes are (r,c) cells; encode as r*cols+c or use a 2D dist array.\n"
        "• State-augmented — add extra state to the node tuple (e.g. stops_remaining).\n"
        "• All-pairs — run Dijkstra from every node: O(V·(V+E) log V)."
    ),
    "pitfalls": (
        "• Always skip stale entries: if d > dist[u]: continue.\n"
        "• Negative weights → Dijkstra gives wrong results; use Bellman-Ford.\n"
        "• K-stops constraint (Cheapest Flights): plain Dijkstra fails — add stops_remaining\n"
        "  to the node state, or use Bellman-Ford (simpler)."
    ),
    "edge_cases": (
        "• src == dst — dist[dst] = 0 immediately; heap pops src and finds no update.\n"
        "• Disconnected graph — unreachable nodes keep dist = inf; check before using.\n"
        "• All edge weights zero — Dijkstra degenerates to BFS; still correct.\n"
        "• Dense graph with many stale heap entries — stale-entry guard ensures each node processed once."
    ),
    "confusion": (
        "┌─────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                             │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Bellman-Ford        │ Any negative edge weights? → Bellman-Ford.          │\n"
        "│                     │ All non-negative? → Dijkstra (faster).              │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ BFS                 │ Are all edge weights equal (all 1)? → BFS (O(V+E)). │\n"
        "│                     │ Variable non-negative weights? → Dijkstra.          │\n"
        "└─────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What breaks if there are negative edges?\n"
        "• How would you reconstruct the actual shortest path, not just the distance?\n"
        "• The graph has 10⁶ nodes and 10⁷ edges — is Dijkstra still fast enough?"
    ),
    "time": "O((V + E) log V)",
    "space": "O(V + E)",
    "problems": [
        ("Network Delay Time",               "M"),
        ("Path With Minimum Effort",         "M"),
        ("Cheapest Flights Within K Stops",  "M"),
        ("Find the City",                    "M"),
        ("Swim in Rising Water",             "H"),
    ],
    "related": ["Graphs", "Heap / Priority Queue", "Bellman-Ford", "Network Flow"],
}
