from __future__ import annotations

TOPIC: dict = {
    "title": "Dijkstra",
    "slug": "Dijkstra",
    "recognize": (
        "shortest path, minimum cost, weighted graph,\n"
        "non-negative edge weights, network delay, cheapest flights."
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
    "when": (
        "Shortest path in a weighted graph with non-negative edge weights.\n"
        "For negative weights use Bellman-Ford instead."
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
    "pitfalls": (
        "• Always skip stale entries: if d > dist[u]: continue.\n"
        "• Negative weights → Dijkstra gives wrong results; use Bellman-Ford.\n"
        "• K-stops constraint (Cheapest Flights): modified BFS or Bellman-Ford, not Dijkstra."
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
