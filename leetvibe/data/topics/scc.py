from __future__ import annotations

TOPIC: dict = {
    "title": "Strongly Connected Components",
    "slug": "SCC",
    "recognize": (
        "Strongly connected components, critical connections, bridges in a graph,\n"
        "directed graph condensation, 2-SAT, find all SCCs in a directed graph.\n"
        "Keywords: DIRECTED graph, groups where every node can reach every other node in the group."
    ),
    "intuition": (
        "• Two nodes are in the same SCC iff each can reach the other — mutual reachability, not just\n"
        "  one-way connectivity, which is what makes this a directed-graph-specific concept.\n"
        "• low[v] tracks the earliest discovery time reachable from v's subtree via at most one back\n"
        "  edge — if low[v] == disc[v], nothing in v's subtree can escape to an earlier ancestor,\n"
        "  so v roots a complete SCC.\n"
        "• The on-stack check (elif on_stk[w]) is what distinguishes a back edge (same SCC) from a\n"
        "  cross edge to an already-finished, different SCC — both look like 'already visited'."
    ),
    "diagram": (
        "  Directed graph:\n"
        "  0 → 1 → 2 → 0    ← SCC {0,1,2}\n"
        "          ↓\n"
        "          3 → 4    ← SCC {3}, SCC {4}\n"
        "\n"
        "  Tarjan's — single DFS pass:\n"
        "  Each node gets: disc[v] (discovery time) and low[v]\n"
        "  low[v] = min discovery reachable from subtree of v\n"
        "  SCC root: disc[v] == low[v] → pop stack up to v\n"
        "\n"
        "  Kosaraju's — two DFS passes:\n"
        "  Pass 1: DFS on G, push nodes in finish order\n"
        "  Pass 2: DFS on G-transpose in reverse finish order"
    ),
    "patterns": [
        {
            "name": "Tarjan's SCC — one DFS, O(V+E)",
            "code": (
                "import sys\n"
                "from collections import defaultdict\n"
                "\n"
                "def tarjan_scc(n, graph):\n"
                "    disc   = [-1] * n     # discovery time (-1 = unvisited)\n"
                "    low    = [0]  * n     # lowest disc reachable\n"
                "    on_stk = [False] * n\n"
                "    stack  = []\n"
                "    timer  = [0]\n"
                "    sccs   = []\n"
                "\n"
                "    def dfs(v):\n"
                "        disc[v] = low[v] = timer[0]; timer[0] += 1\n"
                "        stack.append(v); on_stk[v] = True\n"
                "        for w in graph[v]:\n"
                "            if disc[w] == -1:\n"
                "                dfs(w)\n"
                "                low[v] = min(low[v], low[w])\n"
                "            elif on_stk[w]:\n"
                "                low[v] = min(low[v], disc[w])\n"
                "        if low[v] == disc[v]:          # v is SCC root\n"
                "            scc = []\n"
                "            while True:\n"
                "                w = stack.pop(); on_stk[w] = False\n"
                "                scc.append(w)\n"
                "                if w == v: break\n"
                "            sccs.append(scc)\n"
                "\n"
                "    sys.setrecursionlimit(10**5)\n"
                "    for v in range(n):\n"
                "        if disc[v] == -1: dfs(v)\n"
                "    return sccs"
            ),
        },
        {
            "name": "Critical Connections (Bridges) — Tarjan variant",
            "code": (
                "# A bridge is an edge whose removal disconnects the graph\n"
                "# Use low[v] > disc[u] condition instead of SCC root condition\n"
                "def critical_connections(n, connections):\n"
                "    graph = defaultdict(list)\n"
                "    for u, v in connections:\n"
                "        graph[u].append(v); graph[v].append(u)\n"
                "\n"
                "    disc = [-1] * n\n"
                "    low  = [0]  * n\n"
                "    timer = [0]\n"
                "    bridges = []\n"
                "\n"
                "    def dfs(v, parent):\n"
                "        disc[v] = low[v] = timer[0]; timer[0] += 1\n"
                "        for w in graph[v]:\n"
                "            if disc[w] == -1:\n"
                "                dfs(w, v)\n"
                "                low[v] = min(low[v], low[w])\n"
                "                if low[w] > disc[v]:   # bridge condition\n"
                "                    bridges.append([v, w])\n"
                "            elif w != parent:\n"
                "                low[v] = min(low[v], disc[w])\n"
                "\n"
                "    sys.setrecursionlimit(10**5)\n"
                "    for v in range(n):\n"
                "        if disc[v] == -1: dfs(v, -1)\n"
                "    return bridges"
            ),
        },
    ],
    "variants": (
        "• Tarjan's SCC — single DFS pass using disc/low arrays; fastest in practice.\n"
        "• Kosaraju's SCC — two DFS passes (finish order, then transpose graph); easier to reason about.\n"
        "• Critical Connections (bridges) — Tarjan variant; condition is low[w] > disc[v] (strict).\n"
        "• Articulation points (cut vertices) — Tarjan variant; condition is low[w] >= disc[v].\n"
        "• Condensation graph — collapse each SCC to one node; the result is always a DAG.\n"
        "• 2-SAT — build an implication graph; a variable and its negation in the same SCC → UNSAT."
    ),
    "pitfalls": (
        "• on_stk[] tracks nodes currently on the stack — different from visited[]; a back edge to\n"
        "  a finished (popped) node must NOT update low[].\n"
        "• Bridge finding: track parent to avoid treating the tree edge back to it as a back edge\n"
        "  (undirected graphs only — SCC itself is for directed graphs).\n"
        "• Recursion depth: always sys.setrecursionlimit(10**5) or convert to iterative DFS for large graphs.\n"
        "• Kosaraju is easier to reason about; Tarjan is one pass and faster in practice."
    ),
    "edge_cases": (
        "• Single node, no edges — it is its own SCC of size 1.\n"
        "• Fully connected graph (complete digraph) — the whole graph is one SCC.\n"
        "• DAG with no cycles — every node is its own SCC (n SCCs total).\n"
        "• Self-loop on a node — doesn't merge it with any other node; still its own SCC unless\n"
        "  otherwise connected."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Union Find          │ Graph is undirected, just need component grouping? →  │\n"
        "│                     │ Union Find. Graph is DIRECTED and you need mutual     │\n"
        "│                     │ reachability groups? → Strongly Connected Components. │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why doesn't Union Find work directly on a directed graph for this?\n"
        "• How would you build the condensation DAG from the SCCs?\n"
        "• What's the difference between the bridge condition and the SCC-root condition?\n"
        "• How would you detect if 2-SAT constraints are satisfiable using SCCs?"
    ),
    "time": "O(V + E)",
    "space": "O(V)  disc / low / stack arrays",
    "problems": [
        ("Critical Connections in a Network", "H"),
        ("Number of Strongly Connected Components", "M"),
        ("Longest Cycle in a Graph",           "H"),
        ("Maximum Employees to Be Invited to a Meeting", "H"),
    ],
    "related": ["Graphs", "Topological Sort", "Union Find", "Eulerian Path / Circuit"],
}
