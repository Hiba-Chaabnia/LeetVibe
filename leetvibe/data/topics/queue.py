from __future__ import annotations

TOPIC: dict = {
    "title": "Queue",
    "slug": "Queue",
    "recognize": (
        "FIFO processing, BFS (already uses deque), sliding window with\n"
        "index tracking, first non-repeating, moving average from stream."
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
    "when": (
        "Any FIFO-ordered processing: BFS, sliding window tracking by index,\n"
        "moving average, first unique character in a stream."
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
    "pitfalls": (
        "• Use collections.deque, NOT a list — list.pop(0) is O(n).\n"
        "• deque maxlen parameter auto-evicts from the left when full — handy\n"
        "  for fixed-size sliding windows but hides the eviction logic.\n"
        "• For BFS always add to visited BEFORE enqueuing, not after dequeuing."
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
