from __future__ import annotations

TOPIC: dict = {
    "title": "Queue",
    "slug": "Queue",
    "recognize": (
        "FIFO processing, BFS level tracking, moving average from stream,\n"
        "first non-repeating character, sliding window with index eviction.\n"
        "Any time 'process in arrival order' — reach for deque."
    ),
    "intuition": (
        "• deque gives O(1) append and popleft. list.pop(0) is O(n) and silently\n"
        "  degrades BFS and sliding windows from O(n) to O(n²). Always use deque.\n"
        "• Maintain a running sum for moving average — re-summing the window each\n"
        "  call turns O(1) into O(size) unnecessarily.\n"
        "• For first non-repeating: keep candidates in arrival order, evict from front\n"
        "  as soon as their frequency exceeds 1."
    ),
    "diagram": (
        "  deque (double-ended queue):\n"
        "  appendleft / popleft  ←  [1, 2, 3, 4]  →  append / pop\n"
        "\n"
        "  Queue (FIFO):   enqueue = append      dequeue = popleft\n"
        "  Stack (LIFO):   push    = append      pop     = pop\n"
        "  Monotonic deque: maintain order by popping from BOTH ends\n"
        "\n"
        "  collections.deque: O(1) append/popleft — list.pop(0) is O(n)!"
    ),
    "patterns": [
        {
            "name": "Moving Average from Data Stream",
            "code": (
                "from collections import deque\n"
                "\n"
                "# Moving Average from Data Stream\n"
                "class MovingAverage:\n"
                "    def __init__(self, size):\n"
                "        self.size   = size\n"
                "        self.queue  = deque()\n"
                "        self.window_sum = 0\n"
                "\n"
                "    def next(self, val):\n"
                "        if len(self.queue) == self.size:\n"
                "            self.window_sum -= self.queue.popleft()\n"
                "        self.queue.append(val)\n"
                "        self.window_sum += val\n"
                "        return self.window_sum / len(self.queue)"
            ),
        },
        {
            "name": "First Non-Repeating Character in a Stream",
            "code": (
                "from collections import deque, Counter\n"
                "\n"
                "def first_non_repeating(stream):\n"
                "    freq   = Counter()\n"
                "    result = []\n"
                "    q      = deque()       # candidates in arrival order\n"
                "    for ch in stream:\n"
                "        freq[ch] += 1\n"
                "        q.append(ch)\n"
                "        while q and freq[q[0]] > 1:  # evict repeated chars from front\n"
                "            q.popleft()\n"
                "        result.append(q[0] if q else '#')\n"
                "    return ''.join(result)\n"
                "\n"
                "# Design Hit Counter — sliding window with deque of timestamps\n"
                "class HitCounter:\n"
                "    def __init__(self):\n"
                "        self.hits = deque()     # stores (timestamp, count) pairs\n"
                "\n"
                "    def hit(self, timestamp):\n"
                "        if self.hits and self.hits[-1][0] == timestamp:\n"
                "            self.hits[-1] = (timestamp, self.hits[-1][1] + 1)\n"
                "        else:\n"
                "            self.hits.append((timestamp, 1))\n"
                "\n"
                "    def get_hits(self, timestamp):\n"
                "        while self.hits and self.hits[0][0] <= timestamp - 300:\n"
                "            self.hits.popleft()\n"
                "        return sum(c for _, c in self.hits)"
            ),
        },
    ],
    "variants": (
        "• Plain FIFO — deque with append + popleft; use for BFS level tracking.\n"
        "• Bounded queue (moving average) — maintain running sum; evict oldest when full.\n"
        "• Circular buffer — deque(maxlen=k) auto-evicts oldest on append; hides popleft.\n"
        "• Queue from two stacks — push stack + pop stack; O(1) amortised per op.\n"
        "• Priority queue — use heapq (not deque); see Heap topic.\n"
        "• Monotonic deque — see Monotonic Queue topic."
    ),
    "pitfalls": (
        "• Use collections.deque, NOT a list — list.pop(0) is O(n).\n"
        "• deque(maxlen=k) auto-evicts from the left — handy but hides the eviction logic.\n"
        "• BFS: add to visited BEFORE enqueuing, not after dequeuing."
    ),
    "edge_cases": (
        "• Empty deque — popleft() raises IndexError; always check 'if dq:' before popping.\n"
        "• All identical characters in first-non-repeating — queue empties on first repeat; return '#'.\n"
        "• Hit Counter with non-increasing timestamps — the problem guarantees sorted input;\n"
        "  popleft eviction breaks otherwise."
    ),
    "confusion": (
        "┌─────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                             │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Stack               │ Process oldest first (FIFO)? → Queue (popleft).     │\n"
        "│                     │ Process newest first (LIFO)? → Stack (pop).         │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Monotonic Queue     │ Just need FIFO order? → Plain deque.                │\n"
        "│                     │ Need running max/min within a sliding window? → MQ. │\n"
        "└─────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why is list.pop(0) O(n)? How does deque fix this?\n"
        "• Implement a queue using two stacks.\n"
        "• How would you modify Hit Counter to support out-of-order timestamps?"
    ),
    "time": "O(1) append / popleft",
    "space": "O(n)",
    "problems": [
        ("Moving Average from Data Stream",        "E"),
        ("First Unique Character in a String",     "E"),
        ("Design Hit Counter",                     "M"),
        ("Task Scheduler",                         "M"),
        ("Implement Queue using Stacks",           "E"),
        ("Implement Stack using Queues",           "E"),
    ],
    "related": ["Stack", "Sliding Window", "Monotonic Queue"],
}
