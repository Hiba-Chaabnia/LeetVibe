from __future__ import annotations

TOPIC: dict = {
    "title": "Probability DP",
    "slug": "Probability DP",
    "recognize": (
        "probability of reaching state, expected number of steps,\n"
        "knight probability, dice rolls to target,\n"
        "new 21 game, floating-point DP states."
    ),
    "diagram": (
        "  State: dp[i] = probability of being in state i\n"
        "\n"
        "  Knight Probability on k×k board, starting at (r,c), N moves:\n"
        "  dp[step][row][col] = probability of being at (row,col) after step moves\n"
        "\n"
        "  Transition (each of 8 knight moves equally likely):\n"
        "  dp[s+1][nr][nc] += dp[s][r][c] / 8   for each valid (nr,nc)\n"
        "\n"
        "  Answer: sum of dp[N][r][c] for all (r,c) on the board\n"
        "  (probability of still being on the board after N moves)\n"
        "\n"
        "  Space opt: only need current and previous layer → O(k²)"
    ),
    "when": (
        "The state space has probabilities (floats 0..1) instead of counts.\n"
        "Use when: each transition has a fixed probability, and you need\n"
        "either P(reaching state X) or E[steps to reach state X]."
    ),
    "patterns": [
        {
            "name": "Knight Probability in Chessboard",
            "code": (
                "MOVES = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]\n"
                "\n"
                "def knight_probability(n, k, row, col):\n"
                "    # dp[r][c] = probability of being at (r,c) after current step\n"
                "    dp = [[0.0] * n for _ in range(n)]\n"
                "    dp[row][col] = 1.0\n"
                "\n"
                "    for _ in range(k):\n"
                "        new_dp = [[0.0] * n for _ in range(n)]\n"
                "        for r in range(n):\n"
                "            for c in range(n):\n"
                "                if dp[r][c] == 0: continue\n"
                "                for dr, dc in MOVES:\n"
                "                    nr, nc = r + dr, c + dc\n"
                "                    if 0 <= nr < n and 0 <= nc < n:\n"
                "                        new_dp[nr][nc] += dp[r][c] / 8\n"
                "        dp = new_dp\n"
                "\n"
                "    return sum(dp[r][c] for r in range(n) for c in range(n))"
            ),
        },
        {
            "name": "New 21 Game — probability that score stops in [0, maxPts]",
            "code": (
                "# Player draws cards in [1, maxK] until score >= minK\n"
                "def new21_game(maxPts, minK, maxK):\n"
                "    if minK == 0 or maxPts >= minK + maxK:\n"
                "        return 1.0   # always stays within range\n"
                "\n"
                "    dp = [0.0] * (maxPts + 1)\n"
                "    dp[0] = 1.0\n"
                "    window_sum = 1.0   # sum of dp[i-maxK .. i-1] (sliding window)\n"
                "    result = 0.0\n"
                "\n"
                "    for i in range(1, maxPts + 1):\n"
                "        dp[i] = window_sum / maxK\n"
                "        if i >= minK:              # game stops here — add to result\n"
                "            result += dp[i]\n"
                "        if i >= maxK:              # slide window\n"
                "            window_sum -= dp[i - maxK]\n"
                "        if i < minK:               # game still running — add to window\n"
                "            window_sum += dp[i]\n"
                "    return result"
            ),
        },
    ],
    "pitfalls": (
        "• Floating-point errors accumulate — use Python's float (64-bit) which\n"
        "  is usually sufficient; don't use integer arithmetic.\n"
        "• dp[state] = 0 is fine to skip for performance, but initialise all to 0.0.\n"
        "• Space optimisation: if only the previous step matters, keep just two layers.\n"
        "• New 21 Game uses a sliding window sum to compute dp[i] in O(1) per step\n"
        "  instead of O(maxK) — the key optimisation to hit O(n) total."
    ),
    "time": "O(k × n²) knight  /  O(maxPts) New 21",
    "space": "O(n²) knight  /  O(maxPts) New 21",
    "problems": [
        ("Knight Probability in Chessboard", "M"),
        ("New 21 Game",                      "H"),
        ("Soup Servings",                    "M"),
        ("Dice Roll Simulation",             "H"),
        ("Probability of a Path",            "M"),
    ],
    "related": ["Dynamic Programming", "Math Patterns"],
}
