from __future__ import annotations

TOPIC: dict = {
    "title": "Monotonic Queue",
    "slug": "Monotonic Queue",
    "recognize": (
        "Sliding window maximum / minimum, maximum in window of size k, Jump Game VI, shortest subarray with sum ≥ k.\n"
        "Signal: need O(1) window max/min as the window slides — a heap is too slow."
    ),
    "intuition": (
        "• Any element in the window that is smaller than the new arrival can NEVER be the future window max — evict it now.\n"
        "• The deque stores indices in decreasing-value order; the front is always the current window maximum.\n"
        "• Each index is pushed once and popped at most once — O(n) total, versus O(n log k) for a heap."
    ),
    "diagram": (
        "  Sliding Window Maximum — window size k=3:\n"
        "  nums:  [1,  3, -1, -3,  5,  3,  6,  7]\n"
        "\n"
        "  deque stores INDICES, front = index of current window max\n"
        "  i=0: deque=[0]         window not full yet\n"
        "  i=1: 3>nums[0] → pop 0, push 1   deque=[1]\n"
        "  i=2: push 2            deque=[1,2]   max=nums[1]=3\n"
        "  i=3: push 3            deque=[1,2,3] max=nums[1]=3\n"
        "  i=4: evict 1 (out of window), 5>all → pop 2,3, push 4  deque=[4]\n"
        "  ...\n"
        "  result: [3, 3, 5, 5, 6, 7]\n"
        "\n"
        "  Invariant: deque is always DECREASING (for max); front = window max."
    ),
    "patterns": [
        {
            "name": "Sliding Window Maximum — O(n) total",
            "code": (
                "from collections import deque\n"
                "\n"
                "dq  = deque()   # stores indices; front = index of window max\n"
                "res = []\n"
                "for i in range(len(nums)):\n"
                "    # evict indices that have fallen outside the window\n"
                "    while dq and dq[0] < i - k + 1:\n"
                "        dq.popleft()\n"
                "    # maintain decreasing order: pop smaller values from the back\n"
                "    while dq and nums[dq[-1]] < nums[i]:\n"
                "        dq.pop()\n"
                "    dq.append(i)\n"
                "    if i >= k - 1:\n"
                "        res.append(nums[dq[0]])\n"
                "return res"
            ),
        },
        {
            "name": "Jump Game VI — max score reaching end (dp + monotonic deque)",
            "code": (
                "from collections import deque\n"
                "\n"
                "dp = [0] * len(nums)\n"
                "dp[0] = nums[0]\n"
                "dq = deque([0])   # indices of dp values, decreasing order\n"
                "\n"
                "for i in range(1, len(nums)):\n"
                "    while dq and dq[0] < i - k:\n"
                "        dq.popleft()\n"
                "    dp[i] = dp[dq[0]] + nums[i]\n"
                "    while dq and dp[dq[-1]] <= dp[i]:\n"
                "        dq.pop()\n"
                "    dq.append(i)\n"
                "\n"
                "return dp[-1]"
            ),
        },
    ],
    "variants": (
        "• Sliding window maximum — decreasing deque (pop back when new ≥ back value).\n"
        "• Sliding window minimum — increasing deque (pop back when new ≤ back value).\n"
        "• DP optimisation (Jump Game VI, Constrained Subsequence Sum) — deque over dp values; window by constraint.\n"
        "• Shortest subarray with sum ≥ k — prefix sums + increasing deque; pop front when prefix diff ≥ k."
    ),
    "pitfalls": (
        "• Store INDICES in the deque, not values — you need indices to check window expiry.\n"
        "• Evict from FRONT (out-of-window) and pop from BACK (dominated smaller values).\n"
        "• Decreasing deque → window max; increasing deque → window min.\n"
        "• Don't confuse with Monotonic Stack — the stack has no window/expiry condition."
    ),
    "edge_cases": (
        "• k = 1 — every element is its own window max; deque holds one index at all times.\n"
        "• k = n — window covers entire array; deque never evicts from front; result is one value.\n"
        "• All identical elements — back-popping uses strict <; identicals are NOT popped; correct.\n"
        "• k > len(nums) — window never fills; guard at i >= k-1 never fires; return []."
    ),
    "confusion": (
        "┌───────────────────────┬──────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                          │\n"
        "├───────────────────────┼──────────────────────────────────────────────────┤\n"
        "│ Monotonic Stack       │ Sliding window with expiry? → Monotonic Queue.   │\n"
        "│                       │ Next-greater/previous-smaller without a window?  │\n"
        "│                       │ → Monotonic Stack.                               │\n"
        "├───────────────────────┼──────────────────────────────────────────────────┤\n"
        "│ Heap (sliding window) │ O(n log k) acceptable? → Min/Max-heap of size k. │\n"
        "│                       │ Need O(n) total? → Monotonic deque.              │\n"
        "└───────────────────────┴──────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why use a deque instead of a heap for this problem?\n"
        "• What changes for sliding window minimum?\n"
        "• Can you solve Shortest Subarray with Sum ≥ K with this pattern?"
    ),
    "time": "O(n)  — each element pushed and popped from deque at most once",
    "space": "O(k)  deque holds at most k indices",
    "problems": [
        ("Sliding Window Maximum",                "H"),
        ("Jump Game VI",                          "M"),
        ("Shortest Subarray with Sum at Least K", "H"),
        ("Constrained Subsequence Sum",           "H"),
        ("Maximum of Minimum for Every Window",   "H"),
    ],
    "related": ["Sliding Window", "Monotonic Stack", "Queue"],
}
