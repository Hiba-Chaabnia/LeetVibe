from __future__ import annotations

TOPIC: dict = {
    "title": "Prefix Sum",
    "slug": "Prefix Sum",
    "recognize": (
        "Range sum query, subarray sum equals k, pivot index, multiple queries on one array.\n"
        "If you're re-summing the same range repeatedly — precompute prefix sums instead."
    ),
    "intuition": (
        "• prefix[r+1] - prefix[l] gives any subarray sum in O(1). The sentinel prefix[0]=0\n"
        "  makes the formula work for l=0 without a special case.\n"
        "• Subarray sum = k: you need prefix[j] - prefix[i] = k, i.e. prefix[i] = prefix[j] - k.\n"
        "  Store counts of past prefixes in a hash map; look up the complement in O(1).\n"
        "• Sliding window only works for non-negative arrays. For negatives, use the hash map."
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
    "patterns": [
        {
            "name": "Build prefix sum — O(n) build, O(1) per query",
            "code": (
                "prefix = [0] * (len(arr) + 1)\n"
                "for i, v in enumerate(arr):\n"
                "    prefix[i + 1] = prefix[i] + v\n"
                "\n"
                "def range_sum(l, r):           # inclusive [l, r]\n"
                "    return prefix[r + 1] - prefix[l]"
            ),
        },
        {
            "name": "Subarray sum equals k — hash map of running prefix sums",
            "code": (
                "from collections import defaultdict\n"
                "count = defaultdict(int, {0: 1})   # seed: empty prefix\n"
                "running, res = 0, 0\n"
                "for v in nums:\n"
                "    running += v\n"
                "    res    += count[running - k]    # seen this prefix before?\n"
                "    count[running] += 1\n"
                "return res"
            ),
        },
    ],
    "variants": (
        "• 1D range sum — prefix array; O(n) build, O(1) query.\n"
        "• Subarray sum = k — running prefix + hash map; O(n) time, O(n) space.\n"
        "• 2D range sum — prefix[i][j] = rectangle [0..i-1][0..j-1]; O(1) query, O(mn) build.\n"
        "• Difference array (range update) — delta at l, minus delta at r+1; O(1) update, O(n) rebuild.\n"
        "• Product Except Self — left-prefix × right-suffix products; no division; O(1) extra space.\n"
        "• Contiguous Array (equal 0s and 1s) — replace 0 with -1; find subarray sum = 0 via hash map."
    ),
    "pitfalls": (
        "• Off-by-one: query is prefix[r+1] - prefix[l], not prefix[r] - prefix[l].\n"
        "• Subarray sum = k: seed count[0]=1 BEFORE the loop, not after.\n"
        "• Difference array: add delta at l, subtract at r+1 (not r).\n"
        "• Sliding window doesn't work with negative numbers — use hash map instead."
    ),
    "edge_cases": (
        "• k=0 in subarray sum — subarrays summing to 0 are valid; count[0]=1 handles it.\n"
        "• 2D prefix: inclusion-exclusion is prefix[r2+1][c2+1] - prefix[r1][c2+1]\n"
        "  - prefix[r2+1][c1] + prefix[r1][c1] — forgetting the +corner double-subtracts.\n"
        "• Empty array — prefix = [0]; range query returns 0; no special handling needed."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Sliding Window      │ Need sum of arbitrary [l,r] range in O(1)? → Prefix. │\n"
        "│                     │ Constraint-based expanding/shrinking window? → SW.   │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Segment Tree / BIT  │ Static array (no updates)? → Prefix Sum.             │\n"
        "│                     │ Point updates between queries? → Segment Tree/BIT.   │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you solve subarray sum = k with a sliding window?\n"
        "• How would you handle range sum queries with point updates?\n"
        "• Explain the 2D inclusion-exclusion formula for rectangle sum."
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
