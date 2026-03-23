from __future__ import annotations

TOPIC: dict = {
    "title": "Union Find",
    "slug": "Union Find",
    "recognize": (
        "\"connected components\", \"same group\", \"merge\", \"friends\",\n"
        "  \"redundant connection\", dynamic connectivity queries."
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
    "when": (
        "Detecting connected components, merging groups, or checking\n"
        "  whether two nodes are in the same component."
    ),
    "pattern": (
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
    "pattern2": (
        "# Accounts Merge — Union Find on strings via index mapping\n"
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
    "pitfalls": (
        "• Path compression alone is O(log n); union by rank is needed for O(α(n)).\n"
        "• union() returns False when already connected — use this for cycle detection.\n"
        "• String nodes: map them to integers with a dict before creating the UF.\n"
        "• size[] variant: update size[rx] += size[ry] BEFORE incrementing rank;\n"
        "  use component_size() to answer 'largest island' type follow-ups."
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
