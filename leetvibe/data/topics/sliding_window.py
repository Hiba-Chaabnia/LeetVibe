from __future__ import annotations

TOPIC: dict = {
    "title": "Sliding Window",
    "slug": "Sliding Window",
    "recognize": (
        "contiguous subarray, substring, window,\n"
        "longest/shortest meeting a condition, fixed-size subarray stat."
    ),
    "diagram": (
        "  Variable window (expand right, shrink left when invalid):\n"
        "  a  b  c  d  e  f  g\n"
        "  ↑           ↑\n"
        " left        right        ← expand right each step\n"
        "\n"
        "  window violates condition:\n"
        "     ↑        ↑\n"
        "    left     right        ← shrink: left += 1"
    ),
    "when": (
        "Contiguous subarray or substring of variable or fixed size.\n"
        "Finding longest or shortest window meeting a condition."
    ),
    "patterns": [
        {
            "name": "Variable Window",
            "code": (
                "left = 0\n"
                "window = {}\n"
                "res = 0\n"
                "for right in range(len(s)):\n"
                "    window[s[right]] = window.get(s[right], 0) + 1\n"
                "    while len(window) > k:          # shrink until valid\n"
                "        window[s[left]] -= 1\n"
                "        if window[s[left]] == 0: del window[s[left]]\n"
                "        left += 1\n"
                "    res = max(res, right - left + 1)\n"
                "return res"
            ),
        },
        {
            "name": "Fixed Window",
            "code": (
                "window_sum = sum(nums[:k])\n"
                "best = window_sum\n"
                "for i in range(k, len(nums)):\n"
                "    window_sum += nums[i] - nums[i - k]\n"
                "    best = max(best, window_sum)\n"
                "return best"
            ),
        },
        {
            "name": "Exactly-K Trick",
            "code": (
                "# Direct sliding window can't do 'exactly k' — convert to:\n"
                "#   exactly(k) = atMost(k) - atMost(k - 1)\n"
                "def at_most_k(nums, k):\n"
                "    count = {}\n"
                "    left = res = 0\n"
                "    for right in range(len(nums)):\n"
                "        count[nums[right]] = count.get(nums[right], 0) + 1\n"
                "        while len(count) > k:\n"
                "            count[nums[left]] -= 1\n"
                "            if count[nums[left]] == 0: del count[nums[left]]\n"
                "            left += 1\n"
                "        res += right - left + 1   # all subarrays ending at right\n"
                "    return res\n"
                "\n"
                "def exactly_k(nums, k):\n"
                "    return at_most_k(nums, k) - at_most_k(nums, k - 1)"
            ),
        },
    ],
    "pitfalls": (
        "• Window size formula: right - left + 1 (both ends inclusive).\n"
        "• Fixed window: slide by adding nums[i] and subtracting nums[i-k].\n"
        "• Variable inner while is O(n) amortised — each element enters/leaves once.\n"
        "• 'Exactly k distinct' can't be done directly — use atMost(k) - atMost(k-1)."
    ),
    "time": "O(n)  — each element enters and leaves the window at most once",
    "space": "O(k)  k = window constraint / alphabet size",
    "problems": [
        ("Best Time to Buy and Sell Stock",            "E"),
        ("Longest Substring Without Repeating Chars",  "M"),
        ("Permutation in String",                      "M"),
        ("Longest Repeating Character Replacement",    "M"),
        ("Minimum Window Substring",                   "H"),
        ("Fruit Into Baskets",                         "M"),
        ("Number of Subarrays with Bounded Maximum",   "M"),
    ],
    "related": ["Two Pointers", "Prefix Sum"],
}
