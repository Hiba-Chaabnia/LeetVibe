from __future__ import annotations

TOPIC: dict = {
    "title": "Minimum Spanning Tree",
    "slug": "MST",
    "recognize": (
        "connect all nodes with minimum total cost, minimum cost network,\n"
        "minimum cables to connect cities, undirected weighted graph."
    ),
    "diagram": (
        "  Graph:  A──1──B──4──C\n"
        "          |         |\n"
        "          2         3\n"
        "          |         |\n"
        "          D────5────E\n"
        "\n"
        "  Kruskal: sort edges by weight, greedily add if no cycle (Union Find)\n"
        "  edges sorted: (A-B,1),(A-D,2),(C-E,3),(B-C,4),(D-E,5)\n"
        "  add A-B ✓  add A-D ✓  add C-E ✓  add B-C ✓  stop (n-1 edges)\n"
        "  MST cost = 1+2+3+4 = 10\n"
        "\n"
        "  Prim: grow MST from a seed node, always pick cheapest edge to outside\n"
        "  (same result, different traversal — use min-heap like Dijkstra)"
    ),
    "when": (
        "Connecting all nodes in an undirected weighted graph with minimum\n"
        "total edge weight. Kruskal is simpler to implement with Union Find;\n"
        "Prim is better for dense graphs."
    ),
    "patterns": [
        {
            "name": "Kruskal's Algorithm — sort edges + Union Find",
            "code": (
                "def kruskal(n, edges):\n"
                "    # edges: list of (weight, u, v)\n"
                "    edges.sort()\n"
                "    uf     = UnionFind(n)\n"
                "    mst_cost = 0\n"
                "    mst_edges = []\n"
                "    for weight, u, v in edges:\n"
                "        if uf.union(u, v):           # no cycle — add this edge\n"
                "            mst_cost += weight\n"
                "            mst_edges.append((u, v))\n"
                "            if len(mst_edges) == n - 1:\n"
                "                break               # MST complete\n"
                "    return mst_cost if len(mst_edges) == n - 1 else -1  # -1 = disconnected\n"
                "\n"
                "# UnionFind (reuse from Union Find topic)"
            ),
        },
        {
            "name": "Prim's Algorithm — min-heap, grow from any node",
            "code": (
                "import heapq\n"
                "\n"
                "def prim(n, adj):\n"
                "    # adj[u] = [(weight, v), ...]  (undirected)\n"
                "    visited  = set()\n"
                "    heap     = [(0, 0)]   # (cost, node) — start from node 0\n"
                "    mst_cost = 0\n"
                "    while heap and len(visited) < n:\n"
                "        cost, u = heapq.heappop(heap)\n"
                "        if u in visited: continue\n"
                "        visited.add(u)\n"
                "        mst_cost += cost\n"
                "        for w, v in adj[u]:\n"
                "            if v not in visited:\n"
                "                heapq.heappush(heap, (w, v))\n"
                "    return mst_cost if len(visited) == n else -1"
            ),
        },
    ],
    "pitfalls": (
        "• Kruskal: MST is only possible if the graph is connected — check that\n"
        "  exactly n-1 edges were added; otherwise return -1 or infinity.\n"
        "• Prim: skip already-visited nodes when popping from the heap (same\n"
        "  stale-entry trick as Dijkstra).\n"
        "• MST is for UNDIRECTED graphs — Dijkstra/Bellman-Ford are for directed.\n"
        "• Kruskal O(E log E); Prim with heap O(E log V) — Prim better for dense graphs."
    ),
    "time": "O(E log E) Kruskal  /  O(E log V) Prim",
    "space": "O(V) Union Find  /  O(V + E) adjacency list",
    "problems": [
        ("Min Cost to Connect All Points",    "M"),
        ("Connecting Cities With Minimum Cost","M"),
        ("Optimize Water Distribution",       "H"),
        ("Find Critical and Pseudo-Critical Edges", "H"),
    ],
    "related": ["Graphs", "Union Find", "Dijkstra"],
}
