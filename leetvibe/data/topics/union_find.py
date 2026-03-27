from __future__ import annotations

TOPIC: dict = {
    "title": "Union Find",
    "slug": "Union Find",
    "recognize": (
        "Connected components, same group, merge, friends, redundant connection,\n"
        "dynamic connectivity queries.\n"
        "Keywords: edges/unions arrive incrementally, repeated 'are these in the same group' queries."
    ),
    "intuition": (
        "• Path compression makes find() flatten the tree every time it's called — after enough\n"
        "  calls, almost every node points directly at its root, so future finds are nearly O(1).\n"
        "• Union by rank always attaches the shorter tree under the taller one's root, keeping\n"
        "  worst-case tree height at O(log n) even before compression kicks in.\n"
        "• Together they give amortised O(α(n)) — inverse Ackermann, effectively constant for any\n"
        "  n that fits in memory — far better than re-running BFS/DFS after every new edge."
    ),
    "diagram": (
        "  parent: [0, 1, 2, 3, 4]  (each node is its own root)\n"
        "\n"
        "  union(0,1) → parent[1]=0:   0←1   2   3   4\n"
        "  union(2,3) → parent[3]=2:   0←1   2←3   4\n"
        "  union(0,3) → parent[2]=0:   0←1←(2←3)   4\n"
        "\n"
        "  find(3) with path compression:\n"
        "  3→2→0  then  parent[3]=0, parent[2]=0  (flattened)"
    ),
    "patterns": [
        {
            "name": "Union Find (Path Compression + Union by Rank)",
            "code": (
                "class UnionFind:\n"
                "    def __init__(self, n):\n"
                "        self.parent = list(range(n))\n"
                "        self.rank   = [0] * n\n"
                "        self.size   = [1] * n   # track component sizes\n"
                "        self.count  = n         # number of components\n"
                "\n"
                "    def find(self, x):               # path compression\n"
                "        if self.parent[x] != x:\n"
                "            self.parent[x] = self.find(self.parent[x])\n"
                "        return self.parent[x]\n"
                "\n"
                "    def union(self, x, y):           # union by rank\n"
                "        rx, ry = self.find(x), self.find(y)\n"
                "        if rx == ry: return False    # already connected\n"
                "        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx\n"
                "        self.parent[ry] = rx\n"
                "        self.size[rx]  += self.size[ry]\n"
                "        self.count     -= 1\n"
                "        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1\n"
                "        return True\n"
                "\n"
                "    def connected(self, x, y):\n"
                "        return self.find(x) == self.find(y)\n"
                "\n"
                "    def component_size(self, x):\n"
                "        return self.size[self.find(x)]"
            ),
        },
        {
            "name": "Accounts Merge — Union Find on strings via index mapping",
            "code": (
                "from collections import defaultdict\n"
                "\n"
                "# Map each email to an integer id, then union all emails in an account\n"
                "email_to_id = {}\n"
                "idx = 0\n"
                "for account in accounts:\n"
                "    for email in account[1:]:\n"
                "        if email not in email_to_id:\n"
                "            email_to_id[email] = idx\n"
                "            idx += 1\n"
                "\n"
                "uf = UnionFind(idx)\n"
                "for account in accounts:\n"
                "    root_id = email_to_id[account[1]]\n"
                "    for email in account[2:]:\n"
                "        uf.union(root_id, email_to_id[email])\n"
                "\n"
                "# Collect emails by their root\n"
                "id_to_emails = defaultdict(list)\n"
                "for email, eid in email_to_id.items():\n"
                "    id_to_emails[uf.find(eid)].append(email)\n"
                "\n"
                "# Match root email back to account owner name\n"
                "email_to_name = {account[1]: account[0] for account in accounts}\n"
                "return [[email_to_name[emails[0]]] + sorted(emails)\n"
                "        for emails in id_to_emails.values()]"
            ),
        },
    ],
    "variants": (
        "• Cycle detection (Redundant Connection) — union() returns False on the edge that closes a cycle.\n"
        "• Component counting — count decrements by 1 on every successful union; final count = answer.\n"
        "• Component size tracking — size[] array merged alongside rank; answers 'largest group' queries.\n"
        "• String/object nodes (Accounts Merge) — map to integer ids via a dict before building the UF.\n"
        "• Weighted Union Find — parent[x] stores a relative value/ratio to its root (Evaluate Division)."
    ),
    "pitfalls": (
        "• Path compression alone is O(log n); union by rank is needed for the O(α(n)) bound.\n"
        "• union() returns False when already connected — use this directly for cycle detection.\n"
        "• String nodes: map them to integers with a dict before creating the UF.\n"
        "• size[] variant: update size[rx] += size[ry] BEFORE incrementing rank; use\n"
        "  component_size() to answer 'largest island' type follow-ups."
    ),
    "edge_cases": (
        "• n=1 (single node) — already its own component; count=1, no unions possible.\n"
        "• No edges at all — count stays n; every node is its own component.\n"
        "• Union of a node with itself — find(x)==find(x); union() returns False, no-op.\n"
        "• All nodes already connected — every subsequent union() call returns False (redundant edge)."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Graphs (DFS/BFS     │ Graph is static, one-time component count needed? →  │\n"
        "│ components)         │ plain DFS/BFS, O(V+E) once. Edges/unions arrive      │\n"
        "│                     │ incrementally with repeated 'same group?' queries? → │\n"
        "│                     │ Union Find, near-O(1) per query.                     │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why is union by rank alone not enough — why do you also need path compression?\n"
        "• How would you support 'disconnect' (undo a union)? What breaks?\n"
        "• Accounts Merge: why map emails to integers instead of using them as UF keys directly?\n"
        "• Can Union Find detect a cycle in a DIRECTED graph? Why or why not?"
    ),
    "time": "O(α(n)) ≈ O(1) per operation  (inverse Ackermann)",
    "space": "O(n)",
    "problems": [
        ("Number of Provinces",              "M"),
        ("Redundant Connection",             "M"),
        ("Accounts Merge",                   "M"),
        ("Graph Valid Tree",                 "M"),
        ("Number of Connected Components",   "M"),
        ("Satisfiability of Equality Eqs",   "M"),
    ],
    "related": ["Graphs", "Matrix / Grid", "Strongly Connected Components", "Network Flow"],
}
