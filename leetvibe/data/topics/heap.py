from __future__ import annotations

TOPIC: dict = {
    "title": "Heap / Priority Queue",
    "slug": "Heap (Priority Queue)",
    "recognize": (
        "Top-K elements, K-th largest/smallest, streaming median, merge K sorted lists, task scheduling.\n"
        "Split into lower/upper half → two-heap pattern (median, IPO)."
    ),
    "intuition": (
        "• The heap root is always the min (or max) — O(1) access to the next-best element without sorting everything.\n"
        "• Top-K largest: keep a min-heap of size k; evict the smallest whenever a larger element arrives.\n"
        "• Two-heap median: lo (max-heap) holds the lower half, hi (min-heap) the upper half; median is at the tops."
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
    "patterns": [
        {
            "name": "Heap API (Min / Max / Top-K)",
            "code": (
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
        },
        {
            "name": "Find Median from Data Stream — two heaps",
            "code": (
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
        },
    ],
    "variants": (
        "• Min-heap for smallest — Python's heapq directly.\n"
        "• Max-heap for largest — negate all values on push/pop.\n"
        "• Top-K largest — min-heap of size k; evict when new element > heap[0].\n"
        "• Top-K smallest — max-heap of size k; evict when new element < -heap[0].\n"
        "• Streaming median — two heaps (max lo, min hi); keep sizes equal or lo one larger.\n"
        "• Merge K sorted lists — push (val, list_idx, elem_idx) for each list head; pop min, advance, push next.\n"
        "• Task Scheduler — max-heap of task counts + cooldown queue; execute most frequent available task.\n"
        "• IPO — max-heap of available profits; min-heap of locked projects by capital; unlock as capital grows."
    ),
    "pitfalls": (
        "• Python heapq is min-heap only — negate values for max-heap.\n"
        "• heap[0] peeks without popping; never index beyond [0] in an unsorted heap.\n"
        "• Tuple comparison: heapq compares first element, then second — add a counter to break ties on incomparable values."
    ),
    "edge_cases": (
        "• Empty heap — heappop raises IndexError; guard with len(heap) > 0 or try/except.\n"
        "• k > n in Top-K — return all n elements; nlargest handles this but manual code must guard.\n"
        "• Single element in data stream — lo has one element, hi is empty; find_median returns -lo[0].\n"
        "• Negative values with max-heap negation — negate on BOTH push and pop; missing either silently corrupts."
    ),
    "confusion": (
        "┌───────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                               │\n"
        "├───────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Sorted list / binary  │ K-th element needed once (static)? → Sort + index.    │\n"
        "│ search                │ Streaming inserts with repeated min/max queries?      │\n"
        "│                       │ → Heap O(log n) per op.                               │\n"
        "├───────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Monotonic stack/queue │ Running min/max over a sliding window? → Monotonic    │\n"
        "│                       │ deque O(n).                                           │\n"
        "│                       │ K smallest in an unsorted stream? → Heap.             │\n"
        "└───────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why is heapify O(n) and not O(n log n)?\n"
        "• How would you find the K-th largest in a stream of unknown length with O(k) space?\n"
        "• Two equal priorities cause a comparison error — how do you fix it?"
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
