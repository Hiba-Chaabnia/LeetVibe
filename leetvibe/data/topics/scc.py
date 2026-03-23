from __future__ import annotations

TOPIC: dict = {
    "title": "Strongly Connected Components",
    "slug": "SCC",
    "recognize": (
        "\"strongly connected components\", \"critical connections\",\n"
        "  \"bridges in a graph\", directed graph condensation,\n"
        "  \"2-SAT\", find all SCCs in a directed graph."
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
    "when": (
        "Finding groups of nodes that can all reach each other (directed graph).\n"
        "  Bridge-finding (critical connections), 2-SAT, condensation DAG."
    ),
    "pattern": (
        "# Tarjan's SCC — one DFS, O(V+E)\n"
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
    "pattern2": (
        "# Critical Connections (Bridges) — Tarjan variant\n"
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
    "pitfalls": (
        "• Tarjan SCC: on_stk[] tracks nodes currently on the stack — different\n"
        "  from visited[]; a back edge to a finished node should NOT update low[].\n"
        "• Bridge finding: use parent tracking to avoid treating the tree edge\n"
        "  back to parent as a back edge (undirected graphs).\n"
        "• Recursion depth: always set sys.setrecursionlimit(10**5) or convert to\n"
        "  iterative DFS for large graphs.\n"
        "• Kosaraju is easier to reason about; Tarjan is one pass and faster in practice."
    ),
    "time": "O(V + E)",
    "space": "O(V)  disc / low / stack arrays",
    "problems": [
        ("Critical Connections in a Network", "H"),
        ("Number of Strongly Connected Components", "M"),
        ("Largest Component Size by Comm Factor", "H"),
        ("Course Schedule IV",                 "M"),
    ],
    "related": ["Graphs", "Topological Sort", "Union Find", "Eulerian Path / Circuit"],
}
