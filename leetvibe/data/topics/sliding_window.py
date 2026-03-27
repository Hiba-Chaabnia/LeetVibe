from __future__ import annotations

TOPIC: dict = {
    "title": "Sliding Window",
    "slug": "Sliding Window",
    "recognize": (
        "Contiguous subarray, substring, window, longest/shortest meeting a condition,\n"
        "fixed-size subarray stat.\n"
        "Keywords: CONTIGUOUS (not just any subset), window grows/shrinks as you scan left to right."
    ),
    "intuition": (
        "• Because the window is contiguous, extending right and shrinking left only ever adds or\n"
        "  removes ONE element — the window's aggregate (count, sum) updates in O(1) instead of\n"
        "  being recomputed from scratch.\n"
        "• The left pointer only ever moves forward — once a position is invalid to keep, it's\n"
        "  never valid again as the window grows further, so left never needs to reset backward.\n"
        "• This monotonicity is what gives amortised O(n): each index is added to the window once\n"
        "  (by right) and removed once (by left), for O(n) total pointer movement."
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
    "variants": (
        "• Variable window, longest valid — expand right, shrink left while invalid, track max size.\n"
        "• Variable window, shortest valid — expand right, shrink left WHILE STILL valid, track min size.\n"
        "• Fixed-size window — slide by adding nums[right] and subtracting nums[right-k], O(1) per step.\n"
        "• Exactly-K trick — exactly(k) = atMost(k) - atMost(k-1); direct window can't express 'exactly'.\n"
        "• Two-window / two-pointer hybrid (Minimum Window Substring) — track a need/have count map\n"
        "  alongside the window bounds."
    ),
    "pitfalls": (
        "• Window size formula: right - left + 1 (both ends inclusive).\n"
        "• Fixed window: slide by adding nums[i] and subtracting nums[i-k].\n"
        "• Variable inner while is O(n) amortised — each element enters/leaves the window once.\n"
        "• 'Exactly k distinct' can't be done directly — use atMost(k) - atMost(k-1)."
    ),
    "edge_cases": (
        "• Empty string/array — return 0 immediately; loop body never executes.\n"
        "• k larger than the array length (fixed window) — no valid window exists; guard before the loop.\n"
        "• All elements identical — variable window may grow to cover the whole array; verify shrink\n"
        "  condition still triggers correctly.\n"
        "• Window that never satisfies the condition — result stays at its initial value (0 or infinity)."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Two Pointers        │ Need a CONTIGUOUS run with a size/sum/count           │\n"
        "│                     │ constraint? → Sliding Window. Need a PAIR of elements │\n"
        "│                     │ (not necessarily adjacent) from a sorted structure?   │\n"
        "│                     │ → Two Pointers.                                       │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How would you find the number of subarrays with EXACTLY k distinct elements?\n"
        "• Can you solve Minimum Window Substring in O(n) instead of O(n × alphabet)?\n"
        "• What breaks if the array can contain negative numbers (for a sum-based window)?\n"
        "• How would you adapt this to a circular array?"
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
