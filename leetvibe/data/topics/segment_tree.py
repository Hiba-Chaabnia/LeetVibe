from __future__ import annotations

TOPIC: dict = {
    "title": "Segment Tree",
    "slug": "Segment Tree",
    "recognize": (
        "Range queries WITH point/range updates, range sum after updates, range minimum/maximum,\n"
        "count inversions, mutable prefix sums.\n"
        "Keywords: the array CHANGES over time and you still need fast range queries afterward."
    ),
    "intuition": (
        "• Each internal node stores the aggregate (sum/min/max) of a contiguous range; a query\n"
        "  decomposes the target range into O(log n) pre-aggregated segments instead of scanning.\n"
        "• Updating a leaf only invalidates O(log n) ancestors (its path to the root), so update\n"
        "  and query share the same O(log n) cost — unlike a plain prefix-sum array where an update\n"
        "  invalidates every suffix.\n"
        "• Fenwick Tree exploits the same idea with the binary representation of indices (i & -i)\n"
        "  to implicitly encode the tree in a flat array — same complexity, smaller constant."
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
    "patterns": [
        {
            "name": "Array-based Segment Tree (sum)",
            "code": (
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
        },
        {
            "name": "Fenwick Tree (Binary Indexed Tree) — simpler for prefix sums",
            "code": (
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
        },
    ],
    "variants": (
        "• Sum segment tree — combine as tree[node] = left + right; supports range sum queries.\n"
        "• Min/Max segment tree — combine with min()/max(); same build/update/query shape.\n"
        "• Fenwick Tree (BIT) — simpler point-update + prefix-sum only; smaller constant factor.\n"
        "• Lazy propagation — defer range updates with a pending-delta array; push down on descent.\n"
        "• Merge sort tree — each node stores a sorted list of its range; supports rank queries.\n"
        "• Persistent segment tree — keep every historical version; used for 'k-th smallest over time'."
    ),
    "pitfalls": (
        "• Segment Tree size: allocate 4*n nodes to be safe (2*2^ceil(log2(n))).\n"
        "• Fenwick Tree is 1-indexed — shift all indices by +1 from the array.\n"
        "• Prefer Fenwick Tree when only point updates + prefix queries are needed — simpler to code\n"
        "  and a smaller constant than Segment Tree.\n"
        "• Lazy propagation (range update): store a pending delta at each node, push it down to\n"
        "  children before any query/update that touches them. Without it, range updates cost O(n)."
    ),
    "edge_cases": (
        "• n=1 (single element) — tree has one leaf; build/update/query all degenerate to O(1).\n"
        "• Query range equals the full array — resolves in a single full-overlap call at the root.\n"
        "• Query range outside [0, n-1] — must return the identity element (0 for sum, -inf for max).\n"
        "• Repeated updates to the same index — each update just overwrites; no special handling needed."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Prefix Sum          │ Array is static, queries only? → Prefix Sum, O(1)    │\n"
        "│                     │ per query after O(n) build. Array is MUTATED between │\n"
        "│                     │ queries? → Segment Tree, O(log n) per update/query.  │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why is a plain prefix-sum array wrong once updates are allowed?\n"
        "• When would you choose a Fenwick Tree over a full Segment Tree?\n"
        "• How does lazy propagation change the update complexity for range updates?\n"
        "• Can you support range-min-query AND range-update at the same time?"
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
