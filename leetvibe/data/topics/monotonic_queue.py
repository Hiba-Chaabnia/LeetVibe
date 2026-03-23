from __future__ import annotations

TOPIC: dict = {
    "title": "Monotonic Queue",
    "slug": "Monotonic Queue",
    "recognize": (
        "sliding window maximum / minimum, \"maximum in window of size k\",\n"
        "  \"Jump Game VI\" (max score path), shortest subarray with sum ≥ k."
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
    "when": (
        "Finding the maximum or minimum within a sliding window of fixed size k.\n"
        "  Or any problem needing O(1) window-max after O(n) preprocessing."
    ),
    "pattern": (
        "from collections import deque\n"
        "\n"
        "# Sliding Window Maximum — O(n) total\n"
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
        "    if i >= k - 1:              # window is full\n"
        "        res.append(nums[dq[0]])\n"
        "return res"
    ),
    "pattern2": (
        "# Jump Game VI — max score reaching end (dp + monotonic deque)\n"
        "# dp[i] = max score at index i; can jump up to k steps back\n"
        "from collections import deque\n"
        "\n"
        "dp = [0] * len(nums)\n"
        "dp[0] = nums[0]\n"
        "dq = deque([0])   # indices of dp values, decreasing order\n"
        "\n"
        "for i in range(1, len(nums)):\n"
        "    # evict indices outside the k-step window\n"
        "    while dq and dq[0] < i - k:\n"
        "        dq.popleft()\n"
        "    dp[i] = dp[dq[0]] + nums[i]   # front = best previous index\n"
        "    # maintain decreasing dp order in deque\n"
        "    while dq and dp[dq[-1]] <= dp[i]:\n"
        "        dq.pop()\n"
        "    dq.append(i)\n"
        "\n"
        "return dp[-1]"
    ),
    "pitfalls": (
        "• Store INDICES in the deque, not values — you need indices to check\n"
        "  whether the front element has gone out of the window.\n"
        "• Evict from the FRONT (out-of-window) and pop from the BACK (smaller value).\n"
        "• Decreasing deque → window max; increasing deque → window min.\n"
        "• Don't confuse with Monotonic Stack — the stack doesn't track a window."
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
