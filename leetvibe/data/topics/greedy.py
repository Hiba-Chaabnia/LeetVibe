from __future__ import annotations

TOPIC: dict = {
    "title": "Greedy",
    "slug": "Greedy",
    "recognize": (
        "\"minimum number of\", \"maximum coverage\", interval scheduling,\n"
        "  jump games, \"can reach end\", activity selection."
    ),
    "diagram": (
        "  Activity selection — earliest finish first:\n"
        "  A: ─────────\n"
        "  B:      ─────────    ← A chosen (ends first)\n"
        "  C:           ─────   ← C chosen (next after A)\n"
        "  D:                ── ← D chosen\n"
        "       0   3   5   7   9\n"
        "\n"
        "  local optimum at each step  →  global optimum"
    ),
    "when": (
        "Local optimum reliably leads to global optimum.\n"
        "  Interval scheduling, jump games, fractional knapsack."
    ),
    "pattern": (
        "# Jump Game II — minimum jumps to reach end\n"
        "jumps = farthest = end = 0\n"
        "for i in range(len(nums) - 1):\n"
        "    farthest = max(farthest, i + nums[i])\n"
        "    if i == end:           # must take a jump here\n"
        "        jumps += 1\n"
        "        end = farthest\n"
        "return jumps"
    ),
    "pattern2": (
        "# Gas Station — find starting index\n"
        "# Insight: if total gas >= total cost, a solution always exists.\n"
        "total = tank = start = 0\n"
        "for i in range(len(gas)):\n"
        "    diff   = gas[i] - cost[i]\n"
        "    total += diff\n"
        "    tank  += diff\n"
        "    if tank < 0:    # can't reach i+1 from current start\n"
        "        start = i + 1\n"
        "        tank  = 0\n"
        "return start if total >= 0 else -1\n"
        "\n"
        "# Two City Scheduling — sort by cost DIFFERENCE between two choices\n"
        "# costs[i] = [costA, costB]: send person i to city A or B\n"
        "# Key insight: greedily send the person where the savings vs. the other\n"
        "# city is greatest.  Sort by (costA - costB) ascending: cheapest to\n"
        "# 'upgrade' to A come first; first n go to A, rest go to B.\n"
        "n = len(costs) // 2\n"
        "costs.sort(key=lambda c: c[0] - c[1])\n"
        "return sum(c[0] for c in costs[:n]) + sum(c[1] for c in costs[n:])"
    ),
    "pitfalls": (
        "• Greedy doesn't always work — verify the exchange argument first.\n"
        "• Intervals: sort by END for max non-overlapping; by START for merge.\n"
        "• Jump Game: track farthest reachable index, not just current position.\n"
        "• Sort-by-delta greedy: the key is the DIFFERENCE in cost between the\n"
        "  two options, not the absolute cost of either option alone."
    ),
    "time": "O(n log n) with sorting   /   O(n) otherwise",
    "space": "O(1)",
    "problems": [
        ("Jump Game",          "M"),
        ("Jump Game II",       "M"),
        ("Gas Station",        "M"),
        ("Merge Intervals",    "M"),
        ("Partition Labels",   "M"),
        ("Hand of Straights",  "M"),
    ],
    "related": ["Dynamic Programming", "Intervals"],
}
