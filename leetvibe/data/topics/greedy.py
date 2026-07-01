from __future__ import annotations

TOPIC: dict = {
    "title": "Greedy",
    "slug": "Greedy",
    "recognize": (
        "Minimum jumps, max coverage, interval scheduling, activity selection, gas station, partition labels.\n"
        "Signal: local optimal choice is provably globally optimal — no state needs to be reconsidered."
    ),
    "intuition": (
        "• Greedy works when taking the best local option can never be undone by a later decision.\n"
        "• Prove it with an exchange argument: if any optimal solution skips the greedy choice, swapping it in can't be worse.\n"
        "• If you can't construct that argument, the problem needs DP."
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
    "patterns": [
        {
            "name": "Jump Game II — minimum jumps to reach end",
            "code": (
                "jumps = farthest = end = 0\n"
                "for i in range(len(nums) - 1):\n"
                "    farthest = max(farthest, i + nums[i])\n"
                "    if i == end:           # must take a jump here\n"
                "        jumps += 1\n"
                "        end = farthest\n"
                "return jumps"
            ),
        },
        {
            "name": "Gas Station — find starting index",
            "code": (
                "# If total gas >= total cost, a solution always exists.\n"
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
                "# Two City Scheduling — sort by cost DIFFERENCE\n"
                "# Key: greedily send those with greatest savings to city A.\n"
                "n = len(costs) // 2\n"
                "costs.sort(key=lambda c: c[0] - c[1])\n"
                "return sum(c[0] for c in costs[:n]) + sum(c[1] for c in costs[n:])"
            ),
        },
    ],
    "variants": (
        "• Interval scheduling (max non-overlapping) — sort by end time; greedily pick earliest-finishing non-conflicting.\n"
        "• Merge Intervals — sort by start time; merge if next.start ≤ prev.end.\n"
        "• Jump Game I (can reach end?) — track max reachable index; O(n), O(1).\n"
        "• Jump Game II (minimum jumps) — BFS-like level expansion; count jumps when level ends.\n"
        "• Gas Station — greedy reset: when tank goes negative, restart from next station.\n"
        "• Two City Scheduling — sort by cost difference; first half to A, rest to B.\n"
        "• Partition Labels — extend partition to last occurrence of each character seen; cut when index == end."
    ),
    "pitfalls": (
        "• Greedy doesn't always work — verify the exchange argument or find a counterexample first.\n"
        "• Intervals: sort by END for max non-overlapping; by START for merging.\n"
        "• Jump Game: track farthest REACHABLE, not just current reach — you choose when to jump.\n"
        "• Sort-by-delta: the key is the DIFFERENCE in cost, not the absolute cost of either option."
    ),
    "edge_cases": (
        "• Single element in Jump Game — already at end; return 0 jumps.\n"
        "• No valid solution in Gas Station (total gas < total cost) — return -1; greedy start is invalid.\n"
        "• Identical intervals — merge produces one interval; condition must use ≤ not <.\n"
        "• nums[i] = 0 everywhere in Jump Game — stuck at 0; only reachable if n == 1."
    ),
    "confusion": (
        "┌────────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with    │ Distinguishing question                              │\n"
        "├────────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Dynamic Programming    │ Local choice depends on future sub-problems? → DP.   │\n"
        "│                        │ Exchange argument holds (local = global)? → Greedy.  │\n"
        "├────────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Sorting + two pointers │ After sorting, scanning with two converging indices? │\n"
        "│                        │ → Two Pointers.                                      │\n"
        "│                        │ Single greedy decision per position? → Greedy.       │\n"
        "└────────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How do you prove this greedy is correct and DP isn't needed?\n"
        "• What if intervals have weights — does earliest-finish greedy still work?\n"
        "• Jump Game II: can you prove the greedy gives the minimum jumps?"
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
