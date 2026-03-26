from __future__ import annotations

TOPIC: dict = {
    "title": "Bit Manipulation",
    "slug": "Bit Manipulation",
    "recognize": (
        "Single number, unique among duplicates, count bits, missing number, sum without +, bitmask DP over subsets.\n"
        "Keywords: binary representations, bitmask flags, XOR cancels pairs, subsets as integers."
    ),
    "intuition": (
        "• XOR self-cancels (a ^ a = 0) and has identity 0 (a ^ 0 = a) — XOR-ing pairs leaves only the unique element.\n"
        "• n & (n-1) clears the lowest set bit; repeat until 0 to count bits in O(k) not O(32).\n"
        "• Bitmask DP encodes all 2ⁿ subsets as integers — subset transitions become O(1) bit ops."
    ),
    "diagram": (
        "  AND  &    OR  |    XOR  ^    NOT  ~    SHIFT  <<  >>\n"
        "   1&1=1   1|0=1   1^1=0   ~1=-2   2<<1=4\n"
        "   1&0=0   0|0=0   1^0=1   ~0=-1   8>>1=4\n"
        "\n"
        "  Common tricks:\n"
        "  n & (n-1)      →  clear lowest set bit  (n=0 iff power of 2)\n"
        "  n & (-n)       →  isolate lowest set bit\n"
        "  a ^ b ^ b      →  a   (XOR cancels duplicate pairs)\n"
        "  (i >> k) & 1   →  k-th bit of i\n"
        "  n | (1 << k)   →  set bit k\n"
        "  n & ~(1 << k)  →  clear bit k\n"
        "  n ^ (1 << k)   →  toggle bit k"
    ),
    "patterns": [
        {
            "name": "Count set bits — Brian Kernighan  O(k)",
            "code": (
                "count = 0\n"
                "while n:\n"
                "    n &= n - 1       # clear lowest set bit\n"
                "    count += 1\n"
                "\n"
                "# Find single number (XOR cancels all duplicates)\n"
                "result = 0\n"
                "for num in nums:\n"
                "    result ^= num\n"
                "return result\n"
                "\n"
                "# Power of 2 check — exactly one bit set\n"
                "def is_power_of_two(n):\n"
                "    return n > 0 and (n & (n - 1)) == 0\n"
                "\n"
                "# Missing number\n"
                "result = len(nums)\n"
                "for i, num in enumerate(nums):\n"
                "    result ^= i ^ num\n"
                "return result"
            ),
        },
        {
            "name": "Bitmask DP — enumerate all 2^n subsets",
            "code": (
                "n = len(items)\n"
                "dp = [float('inf')] * (1 << n)\n"
                "dp[0] = 0\n"
                "for mask in range(1 << n):\n"
                "    for i in range(n):\n"
                "        if mask & (1 << i):           # item i is in this subset\n"
                "            prev = mask ^ (1 << i)    # mask without item i\n"
                "            dp[mask] = min(dp[mask], dp[prev] + cost[i])\n"
                "\n"
                "# Enumerate ALL submasks of a given mask — O(3^n) total across all masks\n"
                "# Useful for: subset-sum DP, covering problems\n"
                "submask = mask\n"
                "while submask > 0:\n"
                "    # process submask here\n"
                "    submask = (submask - 1) & mask   # next smaller submask of mask\n"
                "# Note: submask=0 (empty set) is NOT visited by this loop; handle separately\n"
                "\n"
                "# Two unique numbers among duplicates:\n"
                "# XOR all → xor = a ^ b.  Find any differing bit, split array by that bit.\n"
                "xor = 0\n"
                "for num in nums: xor ^= num\n"
                "diff_bit = xor & (-xor)              # isolate rightmost differing bit\n"
                "a = b = 0\n"
                "for num in nums:\n"
                "    if num & diff_bit: a ^= num\n"
                "    else:              b ^= num\n"
                "return [a, b]"
            ),
        },
    ],
    "variants": (
        "• Single number (one unique, rest appear twice) — XOR all elements.\n"
        "• Single number II (one unique, rest appear three times) — track bits mod 3 with two integers.\n"
        "• Two unique numbers — XOR all, isolate a differing bit, partition and XOR each group.\n"
        "• Missing number in [0..n] — XOR all indices and all values; pairs cancel.\n"
        "• Count set bits (array) — DP: dp[i] = dp[i>>1] + (i&1).\n"
        "• Power of 2 — n > 0 and (n & n-1) == 0.\n"
        "• Bitmask DP over subsets — O(n·2ⁿ); feasible only for n ≤ 20.\n"
        "• Submask enumeration — O(3ⁿ) total; use (submask-1)&mask idiom."
    ),
    "pitfalls": (
        "• Python ~n = -(n+1), not a bitwise flip to 0/1 — use (n ^ mask) instead.\n"
        "• Bitmask DP: 2^n states — only feasible for n ≤ 20.\n"
        "• Submask loop: the empty subset (submask=0) is never visited — add it manually.\n"
        "• Power of 2: guard n > 0 before checking n & (n-1) == 0."
    ),
    "edge_cases": (
        "• n = 0 in Brian Kernighan — loop never runs; count = 0. Correct.\n"
        "• n = 0 in power-of-2 check — (0 & -1) == 0 is True; must guard with n > 0.\n"
        "• Negative numbers in XOR problems — XOR works on bit pattern; mask to 32 bits in fixed-width languages.\n"
        "• n > 20 in bitmask DP — 2²⁰ = 1M is fine; 2²⁵ = 33M may OOM."
    ),
    "confusion": (
        "┌──────────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with      │ Distinguishing question                             │\n"
        "├──────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Hash map frequency count │ Do you need O(1) space and the input has a known    │\n"
        "│                          │ duplicate structure (pairs, triples)? → XOR / bits. │\n"
        "│                          │ Arbitrary frequencies or need exact counts? → hash. │\n"
        "├──────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Backtracking subsets     │ Need to enumerate subsets with pruning or ordering  │\n"
        "│                          │ constraints? → backtracking. Need to run DP over    │\n"
        "│                          │ all 2ⁿ subsets in a fixed order? → bitmask DP.      │\n"
        "└──────────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What if every element appears three times except one? Can you still do O(1) space?\n"
        "• How would you add two integers without using + or -?\n"
        "• Your bitmask DP is O(n·2ⁿ) — what's the largest n you could handle in an interview?"
    ),
    "time": "O(1) bitwise ops   /   O(log n) per-bit loops   /   O(2ⁿ) bitmask DP",
    "space": "O(1)   (O(2ⁿ) for bitmask DP)",
    "problems": [
        ("Single Number",          "E"),
        ("Number of 1 Bits",       "E"),
        ("Missing Number",         "E"),
        ("Counting Bits",          "E"),
        ("Reverse Bits",           "E"),
        ("Sum of Two Integers",    "M"),
    ],
    "related": ["Dynamic Programming", "Digit DP", "Game Theory"],
}
