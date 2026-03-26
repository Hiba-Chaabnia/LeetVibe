from __future__ import annotations

TOPIC: dict = {
    "title": "Game Theory",
    "slug": "Game Theory",
    "recognize": (
        "Can the first player win? Nim game, Stone Game, Predict the Winner, Can I Win.\n"
        "Signal: two players alternate turns, both play optimally — win/lose/draw is the answer."
    ),
    "intuition": (
        "• Every position is WIN (current player can force a win) or LOSE (every move hands a win to opponent).\n"
        "• Minimax DP tracks score DIFFERENCE (current − opponent) — opponent's gain is your subtraction.\n"
        "• XOR of pile sizes determines Nim instantly: non-zero XOR → first player wins; zero → loses."
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
    "patterns": [
        {
            "name": "Nim Game — first player wins iff XOR of all pile sizes != 0",
            "code": (
                "from functools import reduce\n"
                "def can_win_nim(piles):\n"
                "    return reduce(lambda a, b: a ^ b, piles) != 0\n"
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
        },
        {
            "name": "Can I Win — bitmask DP over chosen numbers",
            "code": (
                "def stone_game(piles):\n"
                "    return True   # first player always wins with optimal play (math proof)\n"
                "\n"
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
        },
    ],
    "variants": (
        "• Nim (multi-pile, take any from one pile) — XOR of all pile sizes.\n"
        "• Simple Nim (single pile, take 1–k) — n % (k+1) != 0 for first player win.\n"
        "• Misère Nim (last to move loses) — win iff XOR != 0 AND some pile > 1, OR XOR == 0 AND all piles ≤ 1.\n"
        "• Predict the Winner / Stone Game — interval DP minimax; dp[i][j] = max score difference for [i..j].\n"
        "• Stone Game (even piles, first player always wins) — pure math, no DP needed.\n"
        "• Can I Win — bitmask DP over used numbers; O(2ⁿ × n); only for n ≤ ~20.\n"
        "• Complex state games (Stone Game II) — add extra DP dimensions for the current limit."
    ),
    "pitfalls": (
        "• Predict the Winner: dp(i,j) is the DIFFERENCE, not absolute score — opponent's score is subtracted.\n"
        "• Nim XOR: only valid for standard Nim; misère Nim has a different rule.\n"
        "• Can I Win: check total feasibility (sum 1..maxChoosable) before recursing.\n"
        "• Bitmask DP: only feasible for maxChoosable ≤ ~20."
    ),
    "edge_cases": (
        "• desired_total <= 0 in Can I Win — first player wins immediately; return True before recursion.\n"
        "• All zeros in Predict the Winner — dp = 0 everywhere; first player ties (≥ 0) → True.\n"
        "• Single pile of size 0 in Nim — XOR = 0 → second player wins (no valid move for first).\n"
        "• max_choosable = 0 in Can I Win — no numbers available; desired_total > 0 → False."
    ),
    "confusion": (
        "┌──────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with  │ Distinguishing question                             │\n"
        "├──────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Plain interval DP    │ Two players alternating turns, optimal play?        │\n"
        "│                      │ → Game Theory (minimax DP, score difference).       │\n"
        "│                      │ Single agent optimising over an interval? → DP.     │\n"
        "├──────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Bit manipulation XOR │ XOR to cancel duplicate values? → Bit Manipulation. │\n"
        "│                      │ XOR to determine winner of pile-taking game?        │\n"
        "│                      │ → Game Theory (Sprague-Grundy).                     │\n"
        "└──────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Stone Game always returns True — is that really correct? Can you prove it?\n"
        "• Can you solve Predict the Winner bottom-up to avoid recursion depth issues?\n"
        "• What changes for misère Nim (last to move loses)?"
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
