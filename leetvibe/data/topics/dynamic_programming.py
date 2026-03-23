from __future__ import annotations

TOPIC: dict = {
    "title": "Dynamic Programming",
    "slug": "Dynamic Programming",
    "recognize": (
        "\"how many ways\", \"minimum cost\", \"maximum profit\",\n"
        "  overlapping subproblems, optimal substructure, \"longest subsequence\".\n"
        "  Sub-types → \"palindrome\" / \"partition\" = Interval DP;\n"
        "  \"two strings\" / \"edit\" = String DP;\n"
        "  \"stock with cooldown/fee\" = State Machine DP;\n"
        "  \"paint houses\" / \"choose colors\" = Multi-state DP."
    ),
    "diagram": (
        "  Steps to solve any DP problem:\n"
        "  1. Define state:      dp[i] = ?\n"
        "  2. Write transition:  dp[i] = f(dp[i-1], ...)\n"
        "  3. Identify base cases\n"
        "  4. Determine iteration order\n"
        "\n"
        "  Coin Change (unbounded knapsack):\n"
        "  coins=[1,2,5]  amount=6\n"
        "  dp:  [0, 1, 1, 2, 2, 1, 2]   ← dp[6] = 2  (5+1)"
    ),
    "when": (
        "Overlapping subproblems + optimal substructure.\n"
        "  Counting ways, min/max cost, longest subsequences."
    ),
    "pattern": (
        "# Top-down (memoisation) — easiest to write first\n"
        "from functools import cache\n"
        "@cache\n"
        "def dp(i):\n"
        "    if i <= 1: return i              # base case\n"
        "    return dp(i - 1) + dp(i - 2)    # transition\n"
        "\n"
        "# Bottom-up (tabulation)\n"
        "dp = [0] * (n + 1)\n"
        "dp[0], dp[1] = 0, 1\n"
        "for i in range(2, n + 1):\n"
        "    dp[i] = dp[i-1] + dp[i-2]\n"
        "\n"
        "# Space-optimised rolling variables  O(1)\n"
        "a, b = 0, 1\n"
        "for _ in range(2, n + 1):\n"
        "    a, b = b, a + b\n"
        "\n"
        "# ── State Machine DP (Best Time to Buy/Sell with Cooldown) ──────\n"
        "# States: held (own stock), sold (just sold, cooling down), rest (idle)\n"
        "# Transitions each day:\n"
        "#   held  = max(held,       rest - price)   # keep or buy\n"
        "#   sold  = held + price                    # sell today\n"
        "#   rest  = max(rest,       sold)           # cooldown or stay idle\n"
        "held, sold, rest = -float('inf'), 0, 0\n"
        "for price in prices:\n"
        "    prev_held = held\n"
        "    held = max(held,  rest - price)\n"
        "    sold = prev_held + price\n"
        "    rest = max(rest,  sold)\n"
        "return max(sold, rest)\n"
        "# Adapt for 'with fee': sold = prev_held + price - fee\n"
        "# Adapt for 'k transactions': add a third dimension dp[day][k][held]"
    ),
    "pattern2": (
        "# 0/1 Knapsack — iterate capacity in REVERSE so each item used once\n"
        "dp = [0] * (capacity + 1)\n"
        "for weight, value in items:\n"
        "    for w in range(capacity, weight - 1, -1):  # reverse!\n"
        "        dp[w] = max(dp[w], dp[w - weight] + value)\n"
        "\n"
        "# ── String DP ───────────────────────────────────────────────────────\n"
        "# Longest Common Subsequence (2D DP)\n"
        "m, n = len(s1), len(s2)\n"
        "dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
        "for i in range(1, m + 1):\n"
        "    for j in range(1, n + 1):\n"
        "        if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1\n"
        "        else:                   dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n"
        "# return dp[m][n]\n"
        "\n"
        "# ── Regex / Wildcard DP ─────────────────────────────────────────────\n"
        "# Regular Expression Matching  (LC 10):  '.' matches one char, '*' matches\n"
        "# zero or more of preceding element\n"
        "# dp[i][j] = True if s[:i] matches p[:j]\n"
        "def is_match_regex(s, p):\n"
        "    m, n = len(s), len(p)\n"
        "    dp = [[False] * (n + 1) for _ in range(m + 1)]\n"
        "    dp[0][0] = True\n"
        "    for j in range(2, n + 1):           # handle patterns like a*b*\n"
        "        if p[j-1] == '*': dp[0][j] = dp[0][j-2]\n"
        "    for i in range(1, m + 1):\n"
        "        for j in range(1, n + 1):\n"
        "            if p[j-1] == '*':\n"
        "                dp[i][j] = dp[i][j-2]  # '*' matches zero of prev char\n"
        "                if p[j-2] in (s[i-1], '.'):\n"
        "                    dp[i][j] |= dp[i-1][j]  # '*' matches one more char\n"
        "            elif p[j-1] in (s[i-1], '.'):\n"
        "                dp[i][j] = dp[i-1][j-1]\n"
        "    return dp[m][n]\n"
        "\n"
        "# Wildcard Matching (LC 44): '?' matches one char, '*' matches any sequence\n"
        "def is_match_wildcard(s, p):\n"
        "    m, n = len(s), len(p)\n"
        "    dp = [[False] * (n + 1) for _ in range(m + 1)]\n"
        "    dp[0][0] = True\n"
        "    for j in range(1, n + 1):           # '*' can match empty string\n"
        "        if p[j-1] == '*': dp[0][j] = dp[0][j-1]\n"
        "    for i in range(1, m + 1):\n"
        "        for j in range(1, n + 1):\n"
        "            if p[j-1] == '*':\n"
        "                dp[i][j] = dp[i-1][j] or dp[i][j-1]  # match 1+ or 0\n"
        "            elif p[j-1] in (s[i-1], '?'):\n"
        "                dp[i][j] = dp[i-1][j-1]\n"
        "    return dp[m][n]\n"
        "\n"
        "# ── Interval DP ─────────────────────────────────────────────────────\n"
        "# Burst Balloons — pick the LAST balloon popped in each interval\n"
        "nums = [1] + nums + [1]\n"
        "n = len(nums)\n"
        "dp = [[0] * n for _ in range(n)]\n"
        "for length in range(2, n):\n"
        "    for left in range(0, n - length):\n"
        "        right = left + length\n"
        "        for k in range(left + 1, right):\n"
        "            coins = nums[left] * nums[k] * nums[right]\n"
        "            dp[left][right] = max(dp[left][right],\n"
        "                                  coins + dp[left][k] + dp[k][right])\n"
        "# return dp[0][n-1]"
    ),
    "pitfalls": (
        "• 0/1 Knapsack: reverse weight loop so each item is used at most once.\n"
        "  Unbounded (Coin Change): forward loop.\n"
        "• @cache arguments must be hashable — use tuples, not lists.\n"
        "• Regex vs Wildcard: regex '*' means zero-or-more of PRECEDING char;\n"
        "  wildcard '*' means any sequence — completely different transitions.\n"
        "• Regex base case: dp[0][j] = dp[0][j-2] when p[j-1]=='*' (zero occurrences).\n"
        "• 2D space optimisation: LCS/Edit Distance O(m×n) → O(min(m,n)) — keep one row.\n"
        "• Top-down recursion depth: import sys; sys.setrecursionlimit(10**5)."
    ),
    "time": "O(n) 1D   /   O(m × n) 2D   /   O(n × capacity) knapsack",
    "space": "O(n) table  or  O(1) with rolling-array optimisation",
    "problems": [
        ("Climbing Stairs",                     "E"),
        ("House Robber",                        "M"),
        ("Coin Change",                         "M"),
        ("Decode Ways",                         "M"),
        ("Maximum Product Subarray",            "M"),
        ("Longest Increasing Subsequence",      "M"),
        ("Longest Common Subsequence",          "M"),
        ("Word Break",                          "M"),
        ("Partition Equal Subset Sum",          "M"),
        ("Edit Distance",                       "M"),
        ("Regular Expression Matching",         "H"),
        ("Wildcard Matching",                   "H"),
        ("Best Time to Buy/Sell with Cooldown", "M"),
        ("Burst Balloons",                      "H"),
    ],
    "related": ["Backtracking", "Greedy", "Digit DP", "Probability DP", "Game Theory"],
}
