from __future__ import annotations

TOPIC: dict = {
    "title": "Eulerian Path / Circuit",
    "slug": "Eulerian",
    "recognize": (
        "Use every edge exactly once, reconstruct itinerary, valid arrangement of pairs.\n"
        "Signal: path/circuit that visits every EDGE (not vertex) once — check degree conditions first."
    ),
    "intuition": (
        "• When DFS gets stuck (no unused edges), that stuck node belongs at the END of the path — append it.\n"
        "• Backtracking splices completed sub-cycles into the growing path at the correct insertion point.\n"
        "• Reverse the result at the end: Hierholzer builds the path backwards."
    ),
    "diagram": (
        "  Eulerian Circuit exists iff:\n"
        "    Undirected: all vertices have EVEN degree\n"
        "    Directed:   every vertex in-degree == out-degree\n"
        "\n"
        "  Eulerian Path exists iff:\n"
        "    Undirected: exactly 0 or 2 vertices have ODD degree\n"
        "    Directed:   exactly one vertex has out-degree - in-degree = +1 (start)\n"
        "                exactly one vertex has in-degree - out-degree = +1 (end)\n"
        "\n"
        "  Hierholzer's algorithm:\n"
        "  1. Start DFS from any node (or the designated start)\n"
        "  2. Keep going until stuck (no unused edges)\n"
        "  3. Append current node to result, backtrack\n"
        "  4. Result is the path in reverse"
    ),
    "patterns": [
        {
            "name": "Hierholzer's Algorithm — O(E log E) with sorted adjacency lists",
            "code": (
                "from collections import defaultdict\n"
                "\n"
                "def find_itinerary(tickets):\n"
                "    graph = defaultdict(list)\n"
                "    for src, dst in sorted(tickets, reverse=True):  # sort for lex order\n"
                "        graph[src].append(dst)\n"
                "\n"
                "    result = []\n"
                "    stack  = ['JFK']          # start node\n"
                "\n"
                "    while stack:\n"
                "        while graph[stack[-1]]:\n"
                "            stack.append(graph[stack[-1]].pop())\n"
                "        result.append(stack.pop())  # dead-end: add to result\n"
                "\n"
                "    return result[::-1]       # reverse for correct order"
            ),
        },
        {
            "name": "Valid Arrangement of Pairs — general directed Eulerian path",
            "code": (
                "# Find start node: out_degree - in_degree == 1\n"
                "# If no such node exists, any node can be start (circuit)\n"
                "from collections import defaultdict\n"
                "\n"
                "def valid_arrangement(pairs):\n"
                "    graph    = defaultdict(list)\n"
                "    out_deg  = defaultdict(int)\n"
                "    in_deg   = defaultdict(int)\n"
                "\n"
                "    for u, v in pairs:\n"
                "        graph[u].append(v)\n"
                "        out_deg[u] += 1\n"
                "        in_deg[v]  += 1\n"
                "\n"
                "    # Find start: out - in == 1; else any node\n"
                "    start = pairs[0][0]\n"
                "    for node in out_deg:\n"
                "        if out_deg[node] - in_deg[node] == 1:\n"
                "            start = node; break\n"
                "\n"
                "    path, stack = [], [start]\n"
                "    while stack:\n"
                "        while graph[stack[-1]]:\n"
                "            stack.append(graph[stack[-1]].pop())\n"
                "        path.append(stack.pop())\n"
                "\n"
                "    path.reverse()\n"
                "    return [[path[i], path[i+1]] for i in range(len(path)-1)]"
            ),
        },
    ],
    "variants": (
        "• Directed Eulerian circuit — every node has in-degree == out-degree; start anywhere.\n"
        "• Directed Eulerian path — one node with out-in=+1 (start), one with in-out=+1 (end).\n"
        "• Undirected Eulerian circuit — all vertices even degree; remove edges from both adj lists.\n"
        "• Lexicographically smallest (Reconstruct Itinerary) — sort adj lists in reverse; pop() gives smallest.\n"
        "• Existence check only — verify degree conditions in O(V+E); skip Hierholzer's."
    ),
    "pitfalls": (
        "• Check degree conditions before running — if they fail, no Eulerian path exists.\n"
        "• Use iterative Hierholzer (stack), NOT recursion — large graphs overflow Python's call stack.\n"
        "• Lexicographic order: sort adjacency lists in REVERSE so pop() yields the smallest destination."
    ),
    "edge_cases": (
        "• Single edge — path is [u, v]; both nodes have degree 1; it's a path, not a circuit.\n"
        "• Disconnected graph — Eulerian path requires all edges in one connected component; check first.\n"
        "• Duplicate edges (multi-edges) — each edge is an independent list entry; Hierholzer handles correctly.\n"
        "• Degree conditions violated — algorithm terminates early with a partial path; always validate upfront."
    ),
    "confusion": (
        "┌─────────────────────────┬────────────────────────────────────────────────────┐\n"
        "│ Often confused with     │ Distinguishing question                            │\n"
        "├─────────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Hamiltonian path        │ Visit every EDGE once? → Eulerian (poly-time).     │\n"
        "│                         │ Visit every VERTEX once? → Hamiltonian (NP-hard).  │\n"
        "├─────────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Plain DFS / topological │ Is the problem about using every edge exactly once │\n"
        "│ sort                    │ (Eulerian), or about reachability / ordering       │\n"
        "│                         │ (DFS/topo)? The dead-end append-and-backtrack step │\n"
        "│                         │ is unique to Hierholzer.                           │\n"
        "└─────────────────────────┴────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What if there is no valid itinerary — how do you detect that early?\n"
        "• Can Hierholzer's be implemented recursively?\n"
        "• How is this different from finding a Hamiltonian path?"
    ),
    "time": "O(E log E)  (sorting adjacency lists)  /  O(E) Hierholzer itself",
    "space": "O(V + E)",
    "problems": [
        ("Reconstruct Itinerary",        "H"),
        ("Valid Arrangement of Pairs",   "H"),
        ("Cracking the Safe",            "H"),
    ],
    "related": ["Graphs", "Strongly Connected Components", "Stack"],
}
