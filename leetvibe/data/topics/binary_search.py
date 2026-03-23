from __future__ import annotations

TOPIC: dict = {
    "title": "Binary Search",
    "slug": "Binary Search",
    "recognize": (
        "sorted array, \"O(log n) required\", \"minimum / maximum valid answer\",\n"
        "  any monotonic feasibility condition on an answer space."
    ),
    "diagram": (
        "  idx:  0    1    2    3    4    5    6\n"
        "  arr:  1    3    5    7    9   11   13\n"
        "                       ↑\n"
        "                      mid\n"
        "\n"
        "  target < arr[mid]  →  right = mid - 1\n"
        "  target > arr[mid]  →  left  = mid + 1\n"
        "  target = arr[mid]  →  found!\n"
        "\n"
        "  search space halves every iteration  →  O(log n)"
    ),
    "when": (
        "Sorted array, or any monotonic search space.\n"
        "  Finding a value, a boundary, or the min/max valid answer."
    ),
    "pattern": (
        "# Find exact value\n"
        "left, right = 0, len(arr) - 1\n"
        "while left <= right:\n"
        "    mid = left + (right - left) // 2   # avoids overflow\n"
        "    if   arr[mid] == target:  return mid\n"
        "    elif arr[mid] <  target:  left  = mid + 1\n"
        "    else:                     right = mid - 1\n"
        "return -1"
    ),
    "pattern2": (
        "# Binary search on INTEGER answer space — smallest valid answer\n"
        "left, right = lo, hi          # define the answer range\n"
        "while left < right:           # converges to smallest valid\n"
        "    mid = (left + right) // 2\n"
        "    if feasible(mid):         # monotonic: once True, stays True\n"
        "        right = mid           # mid could be the answer\n"
        "    else:\n"
        "        left = mid + 1\n"
        "return left\n"
        "\n"
        "# Binary search on REAL-VALUED answer space\n"
        "# Use when the answer is a float (speed, distance, ratio)\n"
        "# e.g. Minimize Max Distance to Gas Station\n"
        "lo, hi = 0.0, max_possible\n"
        "for _ in range(100):          # ~100 iterations gives 1e-30 precision\n"
        "    mid = (lo + hi) / 2\n"
        "    if feasible(mid):         # check if mid is achievable\n"
        "        hi = mid\n"
        "    else:\n"
        "        lo = mid\n"
        "return lo                     # converged to the minimum feasible value\n"
        "# Alternative termination: while hi - lo > 1e-7: ..."
    ),
    "pitfalls": (
        "• Exact search: left <= right. Boundary search: left < right.\n"
        "• mid = left + (right - left) // 2 prevents integer overflow.\n"
        "• Boundary: when feasible(mid) is True set right=mid (NOT mid-1).\n"
        "• Float answer space: use fixed iteration count (100) not hi-lo>eps —\n"
        "  the eps-based loop can be very slow when lo and hi are large."
    ),
    "time": "O(log n)",
    "space": "O(1)",
    "problems": [
        ("Binary Search",                        "E"),
        ("Search in Rotated Sorted Array",        "M"),
        ("Find Minimum in Rotated Sorted Array",  "M"),
        ("Koko Eating Bananas",                   "M"),
        ("Time Based Key-Value Store",            "M"),
        ("Minimize Max Distance to Gas Station",  "H"),
        ("Median of Two Sorted Arrays",           "H"),
    ],
    "related": ["Two Pointers", "Heap / Priority Queue", "Modified Binary Search", "Ordered Set / SortedList"],
}
