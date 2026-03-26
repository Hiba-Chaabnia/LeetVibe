from __future__ import annotations

TOPIC: dict = {
    "title": "Probability DP",
    "slug": "Probability DP",
    "recognize": (
        "Probability of reaching a state, expected number of steps,\n"
        "knight probability, dice rolls to target, New 21 Game.\n"
        "Signal: state values are floats between 0 and 1, not integer counts."
    ),
    "intuition": (
        "• It's standard DP with float states. Each transition splits probability\n"
        "  proportionally: dp[next] += dp[cur] × (1 / num_transitions).\n"
        "• Invariant: after k steps, dp[state] = exact probability of being there.\n"
        "• Only keep two layers (current and next) — prior steps are never needed again."
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
    "variants": (
        "• Knight Probability — 2D grid DP; roll two layers for O(n²) space.\n"
        "• New 21 Game — 1D DP with sliding window sum; O(maxPts) time and space.\n"
        "• Dice Roll to Target — same structure but integer counts, not probabilities.\n"
        "• Soup Servings — probability that soup A runs out first; DP on (a, b) state.\n"
        "• Expected value DP — dp[state] = 1 + (1/k) × Σ dp[next]; solve as linear system."
    ),
    "pitfalls": (
        "• Use floats, not integers — dp values are probabilities in [0.0, 1.0].\n"
        "• New 21 Game: sliding window sum replaces O(maxK) inner loop → O(n) total.\n"
        "• Skip cells where dp[r][c] == 0 for performance — not needed for correctness."
    ),
    "edge_cases": (
        "• k=0 in Knight Probability — no moves; still on board with prob 1.0; return 1.0.\n"
        "• minK=0 or maxPts >= minK+maxK in New 21 — always in range; return 1.0 early.\n"
        "• Non-uniform transition probabilities — replace /8 with the actual weight per edge."
    ),
    "confusion": (
        "┌──────────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with      │ Distinguishing question                             │\n"
        "├──────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Standard counting DP     │ State values are counts (integers)? → Standard DP.  │\n"
        "│                          │ State values are probabilities (floats)? → Prob DP. │\n"
        "├──────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Simulation / Monte Carlo │ State space tractable for exact DP? → DP.           │\n"
        "│                          │ State space too large? → Monte Carlo (approximate). │\n"
        "└──────────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you compute Knight Probability without the two-layer space optimisation?\n"
        "• Why does New 21 Game use a sliding window instead of summing dp[i-maxK..i-1] directly?\n"
        "• What if transition probabilities are not uniform?"
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
