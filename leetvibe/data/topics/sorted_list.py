from __future__ import annotations

TOPIC: dict = {
    "title": "Ordered Set / SortedList",
    "slug": "SortedList",
    "recognize": (
        "\"dynamic sorted order\", insert + delete + rank in O(log n),\n"
        "  sliding window median, count of smaller numbers, falling squares,\n"
        "  any problem needing a mutable sorted structure."
    ),
    "diagram": (
        "  SortedList  (sortedcontainers — pure Python, O(log n) all ops)\n"
        "\n"
        "  sl = SortedList([3, 1, 4, 1, 5])\n"
        "  → internally: [1, 1, 3, 4, 5]   (always sorted)\n"
        "\n"
        "  sl.add(2)        → [1, 1, 2, 3, 4, 5]   O(log n)\n"
        "  sl.remove(1)     → [1, 2, 3, 4, 5]      O(log n)\n"
        "  sl.bisect_left(3)→ 2  (index of 3)       O(log n)\n"
        "  sl[2]            → 3  (by rank)           O(log n)\n"
        "\n"
        "  Compare: heapq can't delete arbitrary elements; set has no rank query;\n"
        "  sorted() re-sorts everything O(n log n). SortedList does all O(log n)."
    ),
    "when": (
        "You need a sorted collection that changes dynamically and you also\n"
        "  need rank queries (index of element, k-th smallest) or range counts.\n"
        "  For static data use prefix sums; for mutable data use SortedList."
    ),
    "pattern": (
        "from sortedcontainers import SortedList\n"
        "\n"
        "sl = SortedList()          # empty; or SortedList(iterable)\n"
        "sl.add(x)                  # O(log n) insert\n"
        "sl.remove(x)               # O(log n) remove first occurrence; raises if absent\n"
        "sl.discard(x)              # O(log n) remove if present, no error otherwise\n"
        "sl.bisect_left(x)          # O(log n) index of first element >= x\n"
        "sl.bisect_right(x)         # O(log n) index of first element >  x\n"
        "sl[k]                      # O(log n) k-th smallest (0-indexed)\n"
        "sl[-1]                     # O(log n) maximum\n"
        "sl[0]                      # O(log n) minimum\n"
        "count_less = sl.bisect_left(x)              # number of elements < x\n"
        "count_range = sl.bisect_left(hi) - sl.bisect_left(lo)  # elements in [lo, hi)"
    ),
    "pattern2": (
        "# Sliding Window Median using two SortedLists\n"
        "# (cleaner alternative to the two-heaps approach)\n"
        "from sortedcontainers import SortedList\n"
        "\n"
        "def median_sliding_window(nums, k):\n"
        "    sl  = SortedList()\n"
        "    res = []\n"
        "    for i, num in enumerate(nums):\n"
        "        sl.add(num)\n"
        "        if i >= k:\n"
        "            sl.remove(nums[i - k])    # evict element leaving the window\n"
        "        if i >= k - 1:\n"
        "            mid = k // 2\n"
        "            if k % 2 == 1:\n"
        "                res.append(float(sl[mid]))\n"
        "            else:\n"
        "                res.append((sl[mid - 1] + sl[mid]) / 2)\n"
        "    return res\n"
        "\n"
        "# Count of Smaller Numbers After Self\n"
        "from sortedcontainers import SortedList\n"
        "\n"
        "def count_smaller(nums):\n"
        "    sl, result = SortedList(), []\n"
        "    for num in reversed(nums):        # process right to left\n"
        "        result.append(sl.bisect_left(num))  # count elements < num\n"
        "        sl.add(num)\n"
        "    return result[::-1]"
    ),
    "pitfalls": (
        "• sortedcontainers is NOT in the Python standard library — check if\n"
        "  your judge has it (LeetCode does; some others don't).\n"
        "• sl.remove(x) raises ValueError if x is absent — use sl.discard(x) instead.\n"
        "• sl.bisect_left(x) returns an INDEX, not the element — sl[sl.bisect_left(x)].\n"
        "• For problems that need O(log n) rank on integers in a known range,\n"
        "  a Fenwick Tree is a safe fallback if sortedcontainers is unavailable."
    ),
    "time": "O(log n) add / remove / rank",
    "space": "O(n)",
    "problems": [
        ("Sliding Window Median",               "H"),
        ("Count of Smaller Numbers After Self", "H"),
        ("Falling Squares",                     "H"),
        ("My Calendar III",                     "H"),
        ("Find Right Interval",                 "M"),
        ("Contains Duplicate III",              "H"),
    ],
    "related": ["Heap / Priority Queue", "Segment Tree", "Binary Search"],
}
