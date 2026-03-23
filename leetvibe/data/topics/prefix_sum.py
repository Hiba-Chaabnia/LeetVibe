from __future__ import annotations

TOPIC: dict = {
    "title": "Prefix Sum",
    "slug": "Prefix Sum",
    "recognize": (
        "\"subarray sum equals k\", \"range sum query\",\n"
        "  \"find pivot index\", multiple range queries on the same array."
    ),
    "diagram": (
        "  arr:    [ 3,  1,  4,  1,  5 ]\n"
        "  prefix: [ 0,  3,  4,  8,  9, 14 ]   (prefix[0] = 0 sentinel)\n"
        "\n"
        "  sum(arr[l..r])  =  prefix[r+1] - prefix[l]\n"
        "\n"
        "  e.g. sum(arr[1..3]) = prefix[4] - prefix[1]\n"
        "                      =    9       -    3    = 6"
    ),
    "when": (
        "Multiple range-sum queries on a static array.\n"
        "  Counting subarrays whose sum equals a target."
    ),
    "pattern": (
        "# Build prefix sum — O(n) build, O(1) per query\n"
        "prefix = [0] * (len(arr) + 1)\n"
        "for i, v in enumerate(arr):\n"
        "    prefix[i + 1] = prefix[i] + v\n"
        "\n"
        "def range_sum(l, r):           # inclusive [l, r]\n"
        "    return prefix[r + 1] - prefix[l]"
    ),
    "pattern2": (
        "# Subarray sum equals k — hash map of running prefix sums\n"
        "from collections import defaultdict\n"
        "count = defaultdict(int, {0: 1})   # seed: empty prefix\n"
        "running, res = 0, 0\n"
        "for v in nums:\n"
        "    running += v\n"
        "    res    += count[running - k]    # seen this prefix before?\n"
        "    count[running] += 1\n"
        "return res"
    ),
    "pitfalls": (
        "• Off-by-one: use prefix[0]=0 sentinel; query is prefix[r+1]-prefix[l].\n"
        "• Subarray sum = k: seed count[0]=1 BEFORE the loop.\n"
        "• Difference array for range updates: add delta at l, subtract at r+1."
    ),
    "time": "O(n) build  /  O(1) per query",
    "space": "O(n)",
    "problems": [
        ("Range Sum Query - Immutable",      "E"),
        ("Find Pivot Index",                 "E"),
        ("Subarray Sum Equals K",            "M"),
        ("Product of Array Except Self",     "M"),
        ("Contiguous Array",                 "M"),
    ],
    "related": ["Arrays & Hashing", "Sliding Window", "Segment Tree"],
}
