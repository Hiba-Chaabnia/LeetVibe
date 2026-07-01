from __future__ import annotations

TOPIC: dict = {
    "title": "Topological Sort",
    "slug": "Topological Sort",
    "recognize": (
        "Prerequisites, dependency order, build order, course schedule, alien dictionary,\n"
        "directed acyclic graph.\n"
        "Keywords: 'must come before', ordering constraint between pairs, only valid on a DAG."
    ),
    "intuition": (
        "• A node with in-degree 0 has no unmet prerequisites — it's always safe to place next in\n"
        "  the order, and removing it can only reduce its neighbours' in-degrees, never invalidate them.\n"
        "• If every node eventually reaches in-degree 0, there's a valid order; if some remain stuck\n"
        "  above 0 forever, they're part of a cycle — a topological order literally cannot exist there.\n"
        "• The DFS variant works because appending a node to the order only AFTER all its\n"
        "  descendants are finished guarantees every prerequisite already appears earlier once reversed."
    ),
    "diagram": (
        "  DAG:   0 → 1 → 3\n"
        "         ↓       ↑\n"
        "         2 ──────┘\n"
        "\n"
        "  Kahn's BFS — in-degree array:\n"
        "  in-degree: [0, 1, 1, 2]\n"
        "  queue: [0]\n"
        "  → process 0, decrement neighbours → queue [1, 2]\n"
        "  → process 1, decrement 3\n"
        "  → process 2, decrement 3 → in_degree[3]=0, queue [3]\n"
        "  → process 3\n"
        "  order: [0,1,2,3]  |  if len(order) < n → cycle!"
    ),
    "patterns": [
        {
            "name": "Kahn's algorithm (BFS + in-degree)",
            "code": (
                "from collections import deque\n"
                "in_degree = [0] * n\n"
                "graph     = [[] for _ in range(n)]\n"
                "for u, v in edges:                # u must come before v\n"
                "    graph[u].append(v)\n"
                "    in_degree[v] += 1\n"
                "\n"
                "q = deque(i for i in range(n) if in_degree[i] == 0)\n"
                "order = []\n"
                "while q:\n"
                "    node = q.popleft()\n"
                "    order.append(node)\n"
                "    for nei in graph[node]:\n"
                "        in_degree[nei] -= 1\n"
                "        if in_degree[nei] == 0:\n"
                "            q.append(nei)\n"
                "return order if len(order) == n else []   # [] means cycle"
            ),
        },
        {
            "name": "DFS-based topological sort — postorder append then reverse",
            "code": (
                "# state: 0=unvisited  1=in-stack (cycle)  2=done\n"
                "state = [0] * n\n"
                "order = []\n"
                "\n"
                "def dfs(node):\n"
                "    if state[node] == 1: return False   # back edge → cycle\n"
                "    if state[node] == 2: return True    # already processed\n"
                "    state[node] = 1\n"
                "    for nei in graph[node]:\n"
                "        if not dfs(nei): return False\n"
                "    state[node] = 2\n"
                "    order.append(node)                  # append AFTER all descendants\n"
                "    return True\n"
                "\n"
                "for i in range(n):\n"
                "    if state[i] == 0:\n"
                "        if not dfs(i): return []        # cycle detected\n"
                "\n"
                "return order[::-1]                      # reverse postorder = topo order\n"
                "\n"
                "# Longest Path in DAG — topo sort + DP (Parallel Courses)\n"
                "# dp[node] = minimum semesters / steps to reach this node\n"
                "# = longest chain of prerequisites ending at this node\n"
                "in_degree = [0] * n\n"
                "graph     = [[] for _ in range(n)]\n"
                "for u, v in edges:\n"
                "    graph[u].append(v)\n"
                "    in_degree[v] += 1\n"
                "\n"
                "from collections import deque\n"
                "dp = [1] * n                            # each course takes at least 1 step\n"
                "q  = deque(i for i in range(n) if in_degree[i] == 0)\n"
                "while q:\n"
                "    node = q.popleft()\n"
                "    for nei in graph[node]:\n"
                "        dp[nei] = max(dp[nei], dp[node] + 1)\n"
                "        in_degree[nei] -= 1\n"
                "        if in_degree[nei] == 0:\n"
                "            q.append(nei)\n"
                "# Answer = max(dp) if all nodes processed, else -1 (cycle)\n"
                "return max(dp) if sum(in_degree) == 0 else -1"
            ),
        },
    ],
    "variants": (
        "• Kahn's algorithm (BFS + in-degree) — process in-degree-0 nodes first; queue naturally\n"
        "  gives one valid topo order and detects cycles via order length.\n"
        "• DFS-based topo sort — postorder append, then reverse; detects cycles via a 3-state DFS.\n"
        "• Longest path / min steps in a DAG — topo order + DP; dp[nei] updates only after dp[node]\n"
        "  is finalised because prerequisites are processed first.\n"
        "• Lexicographically smallest valid order — Kahn's with a min-heap instead of a plain queue.\n"
        "• Alien Dictionary — build edges from adjacent word comparisons, then topo sort the alphabet."
    ),
    "pitfalls": (
        "• If result length < n, a cycle exists — return [] or False accordingly.\n"
        "• Edge direction: (prereq, course) means prereq → course.\n"
        "• Kahn's is easiest to implement; DFS topo sort appends in postorder.\n"
        "• Longest path DP: update dp[nei] = max(dp[nei], dp[node]+1) during BFS — only correct\n"
        "  because nodes are processed in topological order."
    ),
    "edge_cases": (
        "• Disconnected DAG components — Kahn's queue starts with in-degree-0 nodes from ALL\n"
        "  components, not just one.\n"
        "• Self-loop on a node — in-degree never reaches 0 for it; correctly reported as a cycle.\n"
        "• Single node, no edges — trivially a valid order of length 1.\n"
        "• Multiple valid topological orders — any one is acceptable unless the problem asks for\n"
        "  a specific tie-break (e.g. lexicographically smallest)."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Graphs (DFS cycle   │ Just need to know IF a cycle exists? → plain DFS     │\n"
        "│ detection)          │ cycle check.                                         │\n"
        "│                     │ Need a full valid ORDERING of all nodes respecting   │\n"
        "│                     │ every dependency? → Topological Sort.                │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How do you return the lexicographically smallest valid topological order?\n"
        "• Course Schedule II vs Course Schedule — what changes in your implementation?\n"
        "• How would you detect specifically WHICH edges form the cycle?\n"
        "• Can two different topological orders both be valid for the same DAG? Why?"
    ),
    "time": "O(V + E)",
    "space": "O(V + E)",
    "problems": [
        ("Course Schedule",           "M"),
        ("Course Schedule II",        "M"),
        ("Parallel Courses",          "M"),
        ("Find All Recipes",          "M"),
        ("Alien Dictionary",          "H"),
        ("Sequence Reconstruction",   "M"),
        ("Minimum Height Trees",      "M"),
    ],
    "related": ["Graphs", "Union Find", "Strongly Connected Components"],
}
