from __future__ import annotations

TOPIC: dict = {
    "title": "Game Theory",
    "slug": "Game Theory",
    "recognize": (
        "\"can the first player win?\", \"Nim game\", \"Stone game\",\n"
        "  \"predict the winner\", two players play optimally,\n"
        "  \"can I win\", minimax, take-away games."
    ),
    "diagram": (
        "  Two approaches:\n"
        "\n"
        "  1. XOR / Sprague-Grundy (Nim-like games):\n"
        "     Nim: piles = [3, 4, 5]  →  XOR = 3^4^5 = 2 ≠ 0  → first player wins\n"
        "     Rule: first player wins iff XOR of all pile sizes ≠ 0\n"
        "\n"
        "  2. DP Minimax (turn-based, optimal play):\n"
        "     dp[i][j] = max score difference (current - opponent) for subarray [i,j]\n"
        "     Current player picks left or right, then opponent plays optimally:\n"
        "     dp[i][j] = max(nums[i] - dp[i+1][j],\n"
        "                    nums[j] - dp[i][j-1])"
    ),
    "when": (
        "Two-player zero-sum games where both players play optimally.\n"
        "  Nim/XOR for pile-taking games. DP minimax for sequence/interval games."
    ),
    "pattern": (
        "# Nim Game — first player wins iff XOR of pile sizes != 0\n"
        "def can_win_nim(piles):\n"
        "    return (piles[0] if isinstance(piles, (list,)) else piles) != 0\n"
        "\n"
        "# Simple Nim (single pile, take 1-3 stones):\n"
        "def nim_game(n):\n"
        "    return n % 4 != 0   # first player wins unless n is multiple of 4\n"
        "\n"
        "# Predict the Winner — DP minimax on a sequence\n"
        "from functools import cache\n"
        "\n"
        "def predict_the_winner(nums):\n"
        "    n = len(nums)\n"
        "\n"
        "    @cache\n"
        "    def dp(i, j):\n"
        "        # returns max score DIFFERENCE (current player - opponent) for nums[i..j]\n"
        "        if i == j: return nums[i]\n"
        "        pick_left  = nums[i] - dp(i + 1, j)\n"
        "        pick_right = nums[j] - dp(i, j - 1)\n"
        "        return max(pick_left, pick_right)\n"
        "\n"
        "    return dp(0, n - 1) >= 0   # True if first player wins"
    ),
    "pattern2": (
        "# Stone Game (even number of piles, total always determined)\n"
        "def stone_game(piles):\n"
        "    return True   # first player always wins with optimal play (math proof)\n"
        "\n"
        "# Can I Win — bitmask DP over chosen numbers\n"
        "from functools import cache\n"
        "\n"
        "def can_i_win(max_choosable, desired_total):\n"
        "    if max_choosable * (max_choosable + 1) // 2 < desired_total:\n"
        "        return False  # even if all numbers chosen, can't reach target\n"
        "\n"
        "    @cache\n"
        "    def dp(used_mask, remaining):\n"
        "        for i in range(1, max_choosable + 1):\n"
        "            if used_mask & (1 << i): continue   # already chosen\n"
        "            if i >= remaining: return True       # current player wins\n"
        "            if not dp(used_mask | (1 << i), remaining - i):\n"
        "                return True   # opponent loses from this state\n"
        "        return False          # all moves lead to opponent winning\n"
        "\n"
        "    return dp(0, desired_total)"
    ),
    "pitfalls": (
        "• Predict the Winner: dp(i,j) is the DIFFERENCE, not the absolute score —\n"
        "  returning max(nums[i]-dp(...), nums[j]-dp(...)) handles opponent subtraction.\n"
        "• Nim XOR: works ONLY for standard Nim (pick any amount from one pile);\n"
        "  misère Nim (last to move loses) has a different rule.\n"
        "• Can I Win: check total feasibility (sum of 1..maxChoosable) before recursing.\n"
        "• Bitmask DP: only feasible when maxChoosable ≤ ~20."
    ),
    "time": "O(n²) minimax DP  /  O(2ⁿ × n) bitmask DP",
    "space": "O(n²)  /  O(2ⁿ) bitmask",
    "problems": [
        ("Nim Game",             "E"),
        ("Predict the Winner",   "M"),
        ("Stone Game",           "M"),
        ("Can I Win",            "M"),
        ("Stone Game II",        "M"),
        ("Flip Game II",         "M"),
    ],
    "related": ["Dynamic Programming", "Bit Manipulation", "Math Patterns"],
}
