from __future__ import annotations

TOPIC: dict = {
    "title": "Heap / Priority Queue",
    "slug": "Heap (Priority Queue)",
    "recognize": (
        "top-K elements, K-th largest/smallest, streaming median,\n"
        "  merge K sorted lists, task scheduling, Dijkstra.\n"
        "  \"split into lower/upper half\" → two-heaps (median, IPO)."
    ),
    "diagram": (
        "  min-heap:       1              max-heap (negate):\n"
        "                / \\                            9\n"
        "               3   2                         / \\\n"
        "              / \\ / \\                        7   8\n"
        "             7  4 5  6\n"
        "\n"
        "  push   O(log n)    pop   O(log n)    peek  O(1)\n"
        "  heapify list in-place  →  O(n)"
    ),
    "when": (
        "Top-K elements, streaming medians, task scheduling,\n"
        "  Dijkstra's shortest path, or merging K sorted lists."
    ),
    "pattern": (
        "import heapq\n"
        "\n"
        "# Min-heap (Python default)\n"
        "heap = []\n"
        "heapq.heappush(heap, val)\n"
        "smallest = heapq.heappop(heap)\n"
        "peek = heap[0]\n"
        "\n"
        "# Max-heap: negate values\n"
        "heapq.heappush(heap, -val)\n"
        "largest = -heapq.heappop(heap)\n"
        "\n"
        "# Heapify in-place  O(n)\n"
        "heapq.heapify(arr)\n"
        "\n"
        "# Top K largest  O(n log k)\n"
        "return heapq.nlargest(k, nums)"
    ),
    "pattern2": (
        "# Find Median from Data Stream — two heaps\n"
        "lo = []   # max-heap (negate) — lower half\n"
        "hi = []   # min-heap          — upper half\n"
        "\n"
        "def add_num(num):\n"
        "    heapq.heappush(lo, -num)\n"
        "    heapq.heappush(hi, -heapq.heappop(lo))   # balance\n"
        "    if len(lo) < len(hi):\n"
        "        heapq.heappush(lo, -heapq.heappop(hi))\n"
        "\n"
        "def find_median():\n"
        "    if len(lo) > len(hi): return -lo[0]\n"
        "    return (-lo[0] + hi[0]) / 2"
    ),
    "pitfalls": (
        "• Python heapq is min-heap only — negate values for max-heap.\n"
        "• heap[0] peeks without popping; never index beyond [0] in an unsorted heap.\n"
        "• For (priority, value) tuples, heapq compares the first element, then second."
    ),
    "time": "O(log n) push/pop  /  O(n) heapify  /  O(n log k) top-K",
    "space": "O(k)  for top-K heap",
    "problems": [
        ("Kth Largest Element in an Array", "M"),
        ("K Closest Points to Origin", "M"),
        ("Top K Frequent Elements", "M"),
        ("Task Scheduler", "M"),
        ("IPO", "H"),
        ("Design Twitter", "M"),
        ("Merge K Sorted Lists", "H"),
        ("Find Median from Data Stream", "H"),
    ],
    "related": ["Binary Search", "Dijkstra", "Ordered Set / SortedList"],
}
