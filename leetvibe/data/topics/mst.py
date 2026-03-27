from __future__ import annotations

TOPIC: dict = {
    "title": "Minimum Spanning Tree",
    "slug": "MST",
    "recognize": (
        "Connect all nodes with minimum total cost, minimum cost network,\n"
        "minimum cables to connect cities, undirected weighted graph.\n"
        "Keywords: connect ALL nodes (not just find a path between two), minimise TOTAL edge weight."
    ),
    "intuition": (
        "• Kruskal's is a greedy proof: adding the globally cheapest edge that doesn't create a cycle\n"
        "  never hurts — the cut property guarantees the minimum edge crossing any cut is in SOME MST.\n"
        "• Union Find is what makes 'doesn't create a cycle' an O(α(n)) check instead of a graph search.\n"
        "• Prim's grows one connected blob outward, always picking the cheapest edge leaving the blob —\n"
        "  same greedy guarantee, different bookkeeping (min-heap of frontier edges, like Dijkstra)."
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
    "variants": (
        "• Kruskal's — sort all edges once, greedily union; best for sparse graphs.\n"
        "• Prim's — min-heap grows one tree from a seed node; best for dense graphs.\n"
        "• Minimum cost to connect points (Euclidean) — build all O(n²) edges first, then Kruskal/Prim.\n"
        "• MST with must-include edges — union those first, then run Kruskal on the rest.\n"
        "• Second-best MST — for each MST edge, temporarily exclude it and recompute (O(E) MSTs)."
    ),
    "pitfalls": (
        "• MST only exists if the graph is connected — check exactly n-1 edges were added;\n"
        "  otherwise return -1 or infinity.\n"
        "• Prim: skip already-visited nodes when popping from the heap (same stale-entry\n"
        "  trick as Dijkstra).\n"
        "• MST is for UNDIRECTED graphs — Dijkstra/Bellman-Ford solve directed shortest paths.\n"
        "• Kruskal O(E log E); Prim with heap O(E log V) — Prim is better for dense graphs."
    ),
    "edge_cases": (
        "• Disconnected graph — no spanning tree exists; Kruskal adds < n-1 edges, return -1.\n"
        "• n=1 (single node) — MST cost is 0, no edges needed.\n"
        "• Duplicate-weight edges — any valid MST is acceptable; ties don't affect total cost.\n"
        "• Self-loops — always skip; they can never be part of a spanning tree."
    ),
    "confusion": (
        "┌─────────────────────┬────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                            │\n"
        "├─────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Dijkstra            │ Need cheapest path from ONE source to all nodes? → │\n"
        "│                     │ Dijkstra. Need to connect ALL nodes with minimum   │\n"
        "│                     │ TOTAL edge weight (no single source)? → MST.       │\n"
        "└─────────────────────┴────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why does Dijkstra's greedy choice not work for MST and vice versa?\n"
        "• How would you find the second-minimum spanning tree?\n"
        "• The graph is dense (E ≈ V²) — which algorithm do you pick and why?\n"
        "• How would you handle a graph that must include certain edges?"
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
