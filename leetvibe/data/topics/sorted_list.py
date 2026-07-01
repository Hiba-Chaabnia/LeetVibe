from __future__ import annotations

TOPIC: dict = {
    "title": "Ordered Set / SortedList",
    "slug": "SortedList",
    "recognize": (
        "Dynamic sorted order, insert + delete + rank in O(log n), sliding window median,\n"
        "count of smaller numbers, falling squares, any problem needing a mutable sorted structure.\n"
        "Keywords: elements change over time AND you need order statistics (rank, k-th, range count)."
    ),
    "intuition": (
        "• A balanced sorted structure keeps elements ordered as they're inserted/removed, so\n"
        "  'what index would x have' (bisect_left) is answerable in O(log n) instead of a full sort.\n"
        "• Rank queries (count of elements < x) fall out for free once order is maintained — the\n"
        "  bisect index IS the count.\n"
        "• Unlike a heap (only the extremes are cheap) or a plain sorted array (insert is O(n)),\n"
        "  SortedList keeps EVERY position accessible at O(log n), which is the whole point when\n"
        "  you need both dynamic updates and arbitrary rank/median queries."
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
    "patterns": [
        {
            "name": "SortedList API Reference",
            "code": (
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
        },
        {
            "name": "Sliding Window Median using two SortedLists",
            "code": (
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
        },
    ],
    "variants": (
        "• Rank/order-statistics queries — sl[k] for k-th smallest, bisect_left for count-less-than.\n"
        "• Sliding window median — add/remove at window edges; median from sl[mid] or sl[mid-1:mid+1].\n"
        "• Count of smaller/larger elements — process right-to-left, bisect before each insert.\n"
        "• Range count queries — bisect_left(hi) - bisect_left(lo) for elements in [lo, hi).\n"
        "• Fenwick Tree fallback — when sortedcontainers is unavailable, coordinate-compress values\n"
        "  and use a Fenwick Tree for the same rank/count operations."
    ),
    "pitfalls": (
        "• sortedcontainers is NOT in the Python standard library — check if your judge has it\n"
        "  (LeetCode does; some others don't).\n"
        "• sl.remove(x) raises ValueError if x is absent — use sl.discard(x) instead.\n"
        "• sl.bisect_left(x) returns an INDEX, not the element — sl[sl.bisect_left(x)].\n"
        "• For O(log n) rank on integers in a known range, a Fenwick Tree is a safe fallback\n"
        "  if sortedcontainers is unavailable."
    ),
    "edge_cases": (
        "• Empty SortedList — sl[0] raises IndexError; guard len(sl) > 0 before indexing.\n"
        "• Duplicate values — SortedList keeps all copies; bisect_left/right differ by the run length.\n"
        "• Removing a value not present — sl.remove() raises; use sl.discard() when uncertain.\n"
        "• Window size 1 (sliding window median) — median is simply sl[0], the single element."
    ),
    "confusion": (
        "┌────────────────────────┬────────────────────────────────────────────────────────┐\n"
        "│ Often confused with    │ Distinguishing question                                │\n"
        "├────────────────────────┼────────────────────────────────────────────────────────┤\n"
        "│ Segment Tree / Fenwick │ Values fit a known small range, and you're comfortable │\n"
        "│                        │ coordinate-compressing? → Fenwick Tree.                │\n"
        "│                        │ Need a general-purpose ordered container with minimal  │\n"
        "│                        │ code? → SortedList.                                    │\n"
        "└────────────────────────┴────────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How would you implement this if sortedcontainers weren't available?\n"
        "• Can you find the sliding window median with two heaps instead?\n"
        "• How do you handle duplicate values when computing rank?\n"
        "• What's the time complexity of SortedList's __getitem__ and why is it O(log n), not O(1)?"
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
