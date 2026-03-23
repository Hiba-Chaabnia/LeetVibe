from __future__ import annotations

TOPIC: dict = {
    "title": "Segment Tree",
    "slug": "Segment Tree",
    "recognize": (
        "range queries WITH point/range updates, \"range sum after updates\",\n"
        "  \"range minimum/maximum\", \"count inversions\", mutable prefix sums."
    ),
    "diagram": (
        "  arr = [1, 3, 5, 7, 9, 11]   (n = 6)\n"
        "\n"
        "             [36]              ← sum of full range [0,5]\n"
        "           /       \\\n"
        "        [9]         [27]       ← [0,2] and [3,5]\n"
        "       /   \\       /    \\\n"
        "     [4]   [5]  [16]   [11]   ← [0,1],[2,2],[3,4],[5,5]\n"
        "     / \\\n"
        "   [1] [3]                    ← leaves = arr[0], arr[1]\n"
        "\n"
        "  Node i → children: 2i+1 (left), 2i+2 (right)  (0-indexed)\n"
        "  Build: O(n)   Query: O(log n)   Update: O(log n)"
    ),
    "when": (
        "Range queries (sum, min, max, GCD) on a mutable array.\n"
        "  Prefix sum handles static arrays in O(1); Segment Tree handles\n"
        "  dynamic updates in O(log n). Use a Fenwick Tree for simpler\n"
        "  point-update + prefix-sum queries."
    ),
    "pattern": (
        "# Array-based Segment Tree (sum)\n"
        "class SegTree:\n"
        "    def __init__(self, nums):\n"
        "        self.n    = len(nums)\n"
        "        self.tree = [0] * (4 * self.n)\n"
        "        self._build(nums, 0, 0, self.n - 1)\n"
        "\n"
        "    def _build(self, nums, node, start, end):\n"
        "        if start == end:\n"
        "            self.tree[node] = nums[start]; return\n"
        "        mid = (start + end) // 2\n"
        "        self._build(nums, 2*node+1, start, mid)\n"
        "        self._build(nums, 2*node+2, mid+1, end)\n"
        "        self.tree[node] = self.tree[2*node+1] + self.tree[2*node+2]\n"
        "\n"
        "    def update(self, node, start, end, idx, val):\n"
        "        if start == end:\n"
        "            self.tree[node] = val; return\n"
        "        mid = (start + end) // 2\n"
        "        if idx <= mid: self.update(2*node+1, start, mid,   idx, val)\n"
        "        else:          self.update(2*node+2, mid+1, end,   idx, val)\n"
        "        self.tree[node] = self.tree[2*node+1] + self.tree[2*node+2]\n"
        "\n"
        "    def query(self, node, start, end, l, r):\n"
        "        if r < start or end < l: return 0         # out of range\n"
        "        if l <= start and end <= r: return self.tree[node]  # full overlap\n"
        "        mid = (start + end) // 2\n"
        "        return (self.query(2*node+1, start, mid, l, r) +\n"
        "                self.query(2*node+2, mid+1, end, l, r))"
    ),
    "pattern2": (
        "# Fenwick Tree (Binary Indexed Tree) — simpler for prefix sums\n"
        "# Supports: point update + prefix sum query, both O(log n)\n"
        "class FenwickTree:\n"
        "    def __init__(self, n):\n"
        "        self.n    = n\n"
        "        self.tree = [0] * (n + 1)   # 1-indexed\n"
        "\n"
        "    def update(self, i, delta):      # add delta at position i (1-indexed)\n"
        "        while i <= self.n:\n"
        "            self.tree[i] += delta\n"
        "            i += i & (-i)            # move to next responsible node\n"
        "\n"
        "    def prefix_sum(self, i):         # sum of [1..i]\n"
        "        s = 0\n"
        "        while i > 0:\n"
        "            s += self.tree[i]\n"
        "            i -= i & (-i)            # move to parent\n"
        "        return s\n"
        "\n"
        "    def range_sum(self, l, r):       # sum of [l..r] (1-indexed)\n"
        "        return self.prefix_sum(r) - self.prefix_sum(l - 1)"
    ),
    "pitfalls": (
        "• Segment Tree size: allocate 4*n nodes to be safe (2*2^ceil(log2(n))).\n"
        "• Fenwick Tree is 1-indexed — shift all indices by +1 from the array.\n"
        "• Prefer Fenwick Tree when only point updates + prefix queries are needed;\n"
        "  it is simpler to code and has a smaller constant than Segment Tree.\n"
        "• Lazy propagation (range update): store a pending delta at each node;\n"
        "  push it down to children before any query or update that touches them.\n"
        "  Without lazy propagation, range updates cost O(n) instead of O(log n)."
    ),
    "time": "O(n) build   /   O(log n) update & query",
    "space": "O(n)",
    "problems": [
        ("Range Sum Query - Mutable",           "M"),
        ("Count of Smaller Numbers After Self", "H"),
        ("The Skyline Problem",                 "H"),
        ("My Calendar III",                     "H"),
    ],
    "related": ["Prefix Sum", "Binary Search", "Arrays & Hashing", "Ordered Set / SortedList"],
}
