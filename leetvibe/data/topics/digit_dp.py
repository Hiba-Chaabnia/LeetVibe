from __future__ import annotations

TOPIC: dict = {
    "title": "Digit DP",
    "slug": "Digit DP",
    "recognize": (
        "count numbers in [0, N] satisfying digit constraints,\n"
        "numbers with unique digits, digits at most N,\n"
        "count integers with digit sum = k, digit-level restrictions."
    ),
    "diagram": (
        "  Count integers in [0, N] digit by digit:\n"
        "\n"
        "  N = 3 2 5   (3 digits)\n"
        "  State at each position i:\n"
        "    tight  : are we still bounded by N's digits?\n"
        "    started: have we placed a non-zero digit yet?\n"
        "    + any accumulated constraint (digit sum, distinct digits, ...)\n"
        "\n"
        "  If tight=True: digits[i] can only go up to N[i]\n"
        "  If tight=False: digits[i] can be 0..9 freely\n"
        "\n"
        "  Answer for [L, R] = f(R) - f(L-1)  (prefix counting)"
    ),
    "when": (
        "Counting integers in a range [0, N] or [L, R] that satisfy\n"
        "constraints defined digit by digit. The key signal is that\n"
        "the constraint depends on individual digit values."
    ),
    "patterns": [
        {
            "name": "Digit DP template — count integers in [0, N] with some property",
            "code": (
                "from functools import cache\n"
                "\n"
                "def count_up_to(N: int) -> int:\n"
                "    digits = list(map(int, str(N)))\n"
                "    n = len(digits)\n"
                "\n"
                "    @cache\n"
                "    def dp(pos, tight, started, *state):\n"
                "        \n"
                "        pos     : current digit position (0-indexed)\n"
                "        tight   : True if all previous digits matched N exactly\n"
                "        started : True if we have placed a non-zero digit\n"
                "        state   : problem-specific accumulated constraint\n"
                "        \n"
                "        if pos == n: return 1 if started else 0  # base: valid number\n"
                "        limit  = digits[pos] if tight else 9\n"
                "        total  = 0\n"
                "        for d in range(0, limit + 1):\n"
                "            new_tight   = tight and (d == limit)\n"
                "            new_started = started or (d != 0)\n"
                "            # add new constraint update here, e.g.:\n"
                "            # new_state = update(state, d, new_started)\n"
                "            total += dp(pos + 1, new_tight, new_started)  # + new_state\n"
                "        return total\n"
                "\n"
                "    return dp(0, True, False)\n"
                "\n"
                "# For range [L, R]: count_up_to(R) - count_up_to(L - 1)"
            ),
        },
        {
            "name": "Count Numbers with Unique Digits (no digit appears twice)",
            "code": (
                "from functools import cache\n"
                "\n"
                "def count_numbers_with_unique_digits(n: int) -> int:\n"
                "    if n == 0: return 1\n"
                "    limit = 10**n - 1\n"
                "    digits = list(map(int, str(limit)))\n"
                "    length = len(digits)\n"
                "\n"
                "    @cache\n"
                "    def dp(pos, tight, started, used_mask):\n"
                "        # used_mask: bitmask of which digits (0-9) have been placed\n"
                "        if pos == length: return 1 if started else 0\n"
                "        limit_d = digits[pos] if tight else 9\n"
                "        total   = 0\n"
                "        for d in range(0, limit_d + 1):\n"
                "            if d != 0 and (used_mask >> d) & 1: continue  # digit already used\n"
                "            new_tight    = tight and (d == limit_d)\n"
                "            new_started  = started or (d != 0)\n"
                "            new_mask     = used_mask | (1 << d) if new_started else 0\n"
                "            total       += dp(pos+1, new_tight, new_started, new_mask)\n"
                "        return total\n"
                "\n"
                "    return dp(0, True, False, 0)"
            ),
        },
    ],
    "pitfalls": (
        "• tight flag must be passed per-digit — it's False once any digit is\n"
        "  placed below the corresponding digit of N, True only while matching exactly.\n"
        "• started flag handles leading zeros: '007' should count as 7, not 3 digits.\n"
        "• For range [L, R] queries: compute f(R) - f(L-1); define f(0) = 0 or 1\n"
        "  depending on whether 0 is a valid answer.\n"
        "• @cache state must be hashable — use tuples and booleans, not lists."
    ),
    "time": "O(n × 10 × 2 × 2 × |state|)  where n = number of digits",
    "space": "O(n × |state space|)  memoisation table",
    "problems": [
        ("Count Numbers with Unique Digits",   "M"),
        ("Numbers At Most N Given Digit Set",  "H"),
        ("Digit Count in Range",               "H"),
        ("Non-negative Integers without Consecutive Ones", "H"),
        ("Number of Digit One",                "H"),
    ],
    "related": ["Dynamic Programming", "Bit Manipulation", "Math Patterns"],
}
