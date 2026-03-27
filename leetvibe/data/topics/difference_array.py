from __future__ import annotations

TOPIC: dict = {
    "title": "Difference Array",
    "slug": "Difference Array",
    "recognize": (
        "Add value to a range [l, r], range update then query, car pooling, flight bookings,\n"
        "corporate schedule, batch range increments on an array then a single read pass.\n"
        "Keywords: many range updates arrive first, all reads happen after."
    ),
    "intuition": (
        "• A range update [l,r] += val only changes the RATE OF CHANGE at two points: it starts at l\n"
        "  and reverts at r+1. Recording just those two deltas is O(1), regardless of range length.\n"
        "• Taking the prefix sum of the delta array replays every recorded start/stop exactly once,\n"
        "  reconstructing the fully-updated array in a single O(n) pass.\n"
        "• This only works because updates and reads are separated in time — it's the inverse\n"
        "  operation of prefix sums (which separate static reads from a single build pass)."
    ),
    "diagram": (
        "  Goal: add +3 to indices [1,3] and +1 to [2,4] then read arr\n"
        "\n"
        "  diff:    [0,  0,  0,  0,  0,  0]  (size n+1)\n"
        "  +3 [1,3]: diff[1]+=3, diff[4]-=3\n"
        "  +1 [2,4]: diff[2]+=1, diff[5]-=1\n"
        "  diff:    [0, +3, +1,  0, -3, -1]\n"
        "\n"
        "  prefix sum of diff → actual array:\n"
        "  arr:     [0,  3,  4,  4,  1,  0]\n"
        "            ↑   ↑   ↑   ↑   ↑\n"
        "           i=0  1   2   3   4\n"
        "\n"
        "  O(1) per update  +  O(n) single read pass  =  O(q + n) total"
    ),
    "patterns": [
        {
            "name": "Difference array — range update in O(1), read in O(n)",
            "code": (
                "n = len(arr)\n"
                "diff = [0] * (n + 1)   # size n+1 so diff[n] is safe\n"
                "\n"
                "def range_add(l, r, val):   # add val to arr[l..r] inclusive\n"
                "    diff[l]     += val\n"
                "    diff[r + 1] -= val\n"
                "\n"
                "# Apply all updates first\n"
                "range_add(1, 3, 3)\n"
                "range_add(2, 4, 1)\n"
                "\n"
                "# Reconstruct final array with one prefix-sum pass\n"
                "result = []\n"
                "running = 0\n"
                "for i in range(n):\n"
                "    running += diff[i]\n"
                "    result.append(arr[i] + running)\n"
                "return result"
            ),
        },
        {
            "name": "Car Pooling — difference array on stop indices",
            "code": (
                "# trips: (passengers, from_stop, to_stop); capacity: int\n"
                "def car_pooling(trips, capacity):\n"
                "    max_stop = max(t[2] for t in trips)\n"
                "    diff = [0] * (max_stop + 2)\n"
                "    for passengers, start, end in trips:\n"
                "        diff[start] += passengers\n"
                "        diff[end]   -= passengers    # passengers exit at end, not end+1\n"
                "    current = 0\n"
                "    for delta in diff:\n"
                "        current += delta\n"
                "        if current > capacity: return False\n"
                "    return True\n"
                "\n"
                "# 2D Difference Array — range-update a rectangle in O(1)\n"
                "# Add val to rectangle (r1,c1)..(r2,c2):\n"
                "def rect_add(diff, r1, c1, r2, c2, val):\n"
                "    diff[r1][c1]     += val\n"
                "    diff[r1][c2+1]   -= val\n"
                "    diff[r2+1][c1]   -= val\n"
                "    diff[r2+1][c2+1] += val\n"
                "\n"
                "# Reconstruct 2D array: double prefix sum\n"
                "def reconstruct_2d(diff, rows, cols):\n"
                "    result = [[0]*cols for _ in range(rows)]\n"
                "    for r in range(rows):\n"
                "        for c in range(cols):\n"
                "            result[r][c] = diff[r][c]\n"
                "            if r > 0: result[r][c] += result[r-1][c]\n"
                "            if c > 0: result[r][c] += result[r][c-1]\n"
                "            if r > 0 and c > 0: result[r][c] -= result[r-1][c-1]\n"
                "    return result"
            ),
        },
    ],
    "variants": (
        "• 1D range increment (Range Addition) — diff[l] += val, diff[r+1] -= val.\n"
        "• Car Pooling / Corporate Flight Bookings — stop/day indices as the range; check capacity.\n"
        "• 2D rectangle updates — four-corner inclusion-exclusion; double prefix sum to reconstruct.\n"
        "• Range increment then single point query — still O(n) prefix pass, or O(1) per query if you\n"
        "  precompute the full prefix-sum array once after all updates."
    ),
    "pitfalls": (
        "• Difference array size must be n+1 (not n) so diff[r+1] is always valid even when r == n-1.\n"
        "• Car Pooling: subtract at diff[end], NOT diff[end+1] — passengers exit at the destination\n"
        "  stop, not one stop later.\n"
        "• Only works when ALL updates happen before ALL reads — for interleaved update+query,\n"
        "  use a Segment Tree or Fenwick Tree instead.\n"
        "• 2D difference array: the inclusion-exclusion at corner (r2+1,c2+1) adds back the\n"
        "  doubly-subtracted corner — easy to forget."
    ),
    "edge_cases": (
        "• Zero updates — reconstructed array equals the original input unchanged.\n"
        "• Range covers the whole array [0, n-1] — diff[n] must exist; array sized n+1 handles it.\n"
        "• Overlapping ranges that cancel out — deltas can sum to 0 at a point; still correct.\n"
        "• Single-element range [l, l] — diff[l] += val, diff[l+1] -= val; don't special-case it."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Segment Tree        │ All updates arrive before all reads? → Difference     │\n"
        "│                     │ Array, O(1) per update. Updates and range-sum queries │\n"
        "│                     │ interleaved? → Segment Tree, O(log n) per operation.  │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What if a query needs the array's state BETWEEN two updates, not just at the end?\n"
        "• How would you extend this to 2D rectangle updates?\n"
        "• Can you answer a single point query in O(1) without reconstructing the whole array?\n"
        "• What data structure would you need if updates and reads were interleaved?"
    ),
    "time": "O(1) per range update  /  O(n) to reconstruct",
    "space": "O(n)  difference array",
    "problems": [
        ("Car Pooling",                  "M"),
        ("Corporate Flight Bookings",    "M"),
        ("Range Addition",               "M"),
        ("Shifting Letters II",          "M"),
        ("Describe the Painting",        "M"),
        ("Amount of New Area Painted",   "H"),
    ],
    "related": ["Prefix Sum", "Segment Tree", "Sweep Line"],
}
