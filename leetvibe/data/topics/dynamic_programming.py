from __future__ import annotations

TOPIC: dict = {
    "title": "Dynamic Programming",
    "slug": "Dynamic Programming",
    "recognize": (
        "Keywords: how many ways, minimum cost, maximum profit, longest subsequence.\n"
        "Signal: a naive recursion would recompute the same sub-problem multiple times.\n"
        "Sub-types → palindrome/partition = Interval DP; two strings/edit = String DP;\n"
        "stock with cooldown/fee = State Machine DP; paint houses/colors = Multi-state DP."
    ),
    "intuition": (
        "• Overlapping subproblems: same sub-problem recurs across branches → cache it.\n"
        "• Optimal substructure: the best solution uses the best sub-solutions — so build up.\n"
        "• The 4 steps every time: define state → write transition → base cases → iteration order."
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
    "patterns": [
        {
            "name": "Top-Down (Memoisation)",
            "code": (
                "from functools import cache\n"
                "@cache\n"
                "def dp(i):\n"
                "    if i <= 1: return i              # base case\n"
                "    return dp(i - 1) + dp(i - 2)    # transition"
            ),
        },
        {
            "name": "Bottom-Up (Tabulation)",
            "code": (
                "dp = [0] * (n + 1)\n"
                "dp[0], dp[1] = 0, 1\n"
                "for i in range(2, n + 1):\n"
                "    dp[i] = dp[i-1] + dp[i-2]"
            ),
        },
        {
            "name": "Space-Optimised (Rolling Vars)",
            "code": (
                "a, b = 0, 1\n"
                "for _ in range(2, n + 1):\n"
                "    a, b = b, a + b"
            ),
        },
        {
            "name": "State Machine DP (Stock with Cooldown)",
            "code": (
                "# States: held (own stock), sold (just sold), rest (idle/cooldown)\n"
                "held, sold, rest = -float('inf'), 0, 0\n"
                "for price in prices:\n"
                "    prev_held, prev_sold = held, sold\n"
                "    held = max(held,  rest - price)\n"
                "    sold = prev_held + price\n"
                "    rest = max(rest,  prev_sold)   # yesterday's sale → cooldown today\n"
                "return max(sold, rest)\n"
                "# With fee:  sold = prev_held + price - fee\n"
                "# k trades:  add dimension dp[day][k][held]"
            ),
        },
        {
            "name": "0/1 Knapsack",
            "code": (
                "dp = [0] * (capacity + 1)\n"
                "for weight, value in items:\n"
                "    for w in range(capacity, weight - 1, -1):  # reverse — each item once\n"
                "        dp[w] = max(dp[w], dp[w - weight] + value)"
            ),
        },
        {
            "name": "String DP (LCS)",
            "code": (
                "m, n = len(s1), len(s2)\n"
                "dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
                "for i in range(1, m + 1):\n"
                "    for j in range(1, n + 1):\n"
                "        if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1\n"
                "        else:                   dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n"
                "# return dp[m][n]"
            ),
        },
        {
            "name": "Interval DP (Burst Balloons)",
            "code": (
                "# Pick the LAST balloon popped in each interval — not the first\n"
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
        },
    ],
    "variants": (
        "• 1D linear (Climbing Stairs, House Robber) — dp[i] uses O(1) prior states; compress to vars.\n"
        "• Unbounded knapsack (Coin Change) — forward inner loop; items reusable.\n"
        "• 0/1 knapsack (Partition Equal Subset Sum) — reverse inner loop; each item used once.\n"
        "• String DP / 2D (LCS, Edit Distance) — dp[i][j] over two prefixes; compress to two rows.\n"
        "• Interval DP (Burst Balloons) — iterate by length; O(n³) time, O(n²) space.\n"
        "• State Machine DP (Stock cooldown/fee) — named states updated simultaneously each step.\n"
        "• Digit DP — state: (position, tight_constraint, accumulated_property); counts valid integers.\n"
        "• Bitmask DP — state encodes a subset; see Bit Manipulation topic."
    ),
    "pitfalls": (
        "• 0/1 Knapsack: reverse weight loop. Unbounded (Coin Change): forward loop. Don't swap them.\n"
        "• @cache arguments must be hashable — tuples, not lists.\n"
        "• Regex '*' = zero-or-more of preceding char. Wildcard '*' = any sequence. Different transitions.\n"
        "• Regex base case: dp[0][j] = dp[0][j-2] when p[j-1]=='*' (the zero-occurrences case).\n"
        "• Top-down recursion depth: sys.setrecursionlimit(10**5) if n is large."
    ),
    "edge_cases": (
        "• n=0 or empty input — size the dp array as n+1 to avoid index-out-of-bounds on dp[0].\n"
        "• Coin Change with amount=0 — answer is 0; dp[0]=0 handles this.\n"
        "• All coins larger than amount — dp[amount] stays inf; return -1.\n"
        "• Knapsack item weight > capacity — inner loop range is empty; item is silently skipped."
    ),
    "confusion": (
        "┌─────────────────────┬────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                            │\n"
        "├─────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Greedy              │ Does each local choice provably lead to the global │\n"
        "│                     │ optimum with no look-back? → Greedy.               │\n"
        "│                     │ Do past choices constrain future ones? → DP.       │\n"
        "├─────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Backtracking        │ Need every solution enumerated? → Backtrack.       │\n"
        "│                     │ Just the count or optimal value? → DP.             │\n"
        "└─────────────────────┴────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you do Coin Change in O(1) space?\n"
        "• Your LCS solution is O(m×n) space — can you reduce it?\n"
        "• When would you choose top-down over bottom-up?\n"
        "• What makes a problem unsuitable for DP?"
    ),
    "time": "O(n) 1D   /   O(m × n) 2D   /   O(n × capacity) knapsack",
    "space": "O(n) table  or  O(1) with rolling-variable optimisation",
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
