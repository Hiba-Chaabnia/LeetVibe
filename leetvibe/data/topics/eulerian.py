from __future__ import annotations

TOPIC: dict = {
    "title": "Eulerian Path / Circuit",
    "slug": "Eulerian",
    "recognize": (
        "\"use every edge exactly once\", \"reconstruct itinerary\",\n"
        "  \"valid arrangement of pairs\", \"Chinese postman\",\n"
        "  path/circuit that visits every EDGE (not vertex) once."
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
    "when": (
        "Problems asking to use every edge exactly once.\n"
        "  Reconstruct Itinerary, Valid Arrangement of Pairs.\n"
        "  First check existence conditions; then run Hierholzer's."
    ),
    "pattern": (
        "# Hierholzer's Algorithm — O(E log E) with sorted adjacency lists\n"
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
    "pattern2": (
        "# Valid Arrangement of Pairs — general directed Eulerian path\n"
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
    "pitfalls": (
        "• Check existence before running: if the degree conditions fail,\n"
        "  no Eulerian path/circuit exists — return [] or raise an error.\n"
        "• Hierholzer iterative: use a stack, not recursion — graphs with\n"
        "  many edges will overflow Python's call stack recursively.\n"
        "• Lexicographic order (Reconstruct Itinerary): sort adjacency lists\n"
        "  in REVERSE so pop() yields the smallest destination.\n"
        "• Eulerian PATH vs CIRCUIT: path has two odd-degree nodes; circuit has none."
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
