from __future__ import annotations

TOPIC: dict = {
    "title": "Digit DP",
    "slug": "Digit DP",
    "recognize": (
        "Count numbers in [0, N] satisfying digit constraints, numbers with unique digits,\n"
        "digits at most N, count integers with digit sum = k, digit-level restrictions.\n"
        "Keywords: N can be up to 10^18 — too large to enumerate, but the constraint is per-digit."
    ),
    "intuition": (
        "• N is too big to iterate one-by-one, but every valid number can be BUILT digit by digit —\n"
        "  so memoise over digit position instead of over the number's value.\n"
        "• The 'tight' flag is what makes this DP instead of brute force: once you place a digit\n"
        "  strictly below N's digit at that position, every later digit is free (0-9); only while\n"
        "  tight does N's own digit continue to cap your choices.\n"
        "• 'started' handles leading zeros: '007' is the number 7, so digits placed before the\n"
        "  first non-zero don't count toward digit-position-dependent constraints (like digit count)."
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
                "        # pos     : current digit position (0-indexed)\n"
                "        # tight   : True if all previous digits matched N exactly\n"
                "        # started : True if we have placed a non-zero digit\n"
                "        # state   : problem-specific accumulated constraint\n"
                "        # NOTE: this base case counts [1, N] — the number 0 is\n"
                "        # excluded; add it separately if 0 satisfies the property.\n"
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
                "            new_started = started or (d != 0)\n"
                "            # once started, EVERY digit (0 included) must be unused;\n"
                "            # leading zeros are not digits of the number\n"
                "            if new_started and (used_mask >> d) & 1: continue\n"
                "            new_tight = tight and (d == limit_d)\n"
                "            new_mask  = used_mask | (1 << d) if new_started else 0\n"
                "            total    += dp(pos+1, new_tight, new_started, new_mask)\n"
                "        return total\n"
                "\n"
                "    return dp(0, True, False, 0) + 1   # +1: the number 0 has unique digits"
            ),
        },
    ],
    "variants": (
        "• Count up to N with no extra state — pure digit-count problems (e.g. count of 1s).\n"
        "• Digit sum = k — add running digit-sum to the state tuple.\n"
        "• Unique digits only — add a used_mask bitmask (which of 0-9 appeared) to the state.\n"
        "• No consecutive equal/forbidden digits — add 'last digit placed' to the state.\n"
        "• Range [L, R] — compute f(R) - f(L-1); the same dp() function serves both calls."
    ),
    "pitfalls": (
        "• tight must be passed per-digit — False once any digit is placed below N's digit there,\n"
        "  True only while every digit so far matches N exactly.\n"
        "• started handles leading zeros: '007' should count as the number 7, not 3 digits.\n"
        "• Range [L, R]: compute f(R) - f(L-1); define f(0) explicitly (0 or 1) depending on\n"
        "  whether 0 itself satisfies the property.\n"
        "• @cache state must be hashable — tuples and booleans, not lists; recreate dp() per call\n"
        "  to N (digits differ) or the cache from a previous N silently reuses stale results."
    ),
    "edge_cases": (
        "• N = 0 — the started flag means the template never counts the number 0 itself; decide\n"
        "  whether 0 satisfies the property and add it explicitly (as Unique Digits does with +1).\n"
        "• L = 0 in range [L, R] — f(L-1) = f(-1) is undefined; special-case L=0 as f(R) - f(-1)=0.\n"
        "• All digits of N are 9 (e.g. N=999) — tight stays True the entire recursion on the max path.\n"
        "• Leading zeros never 'started' — an all-zero digit string must return 0, not count as valid."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Dynamic Programming │ State indexes into a fixed array/string? → plain DP.  │\n"
        "│ (generic)           │ State is (digit position, tight bound, started, extra │\n"
        "│                     │ property) counting valid integers? → Digit DP.        │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why can't you just loop from 0 to N and check each number?\n"
        "• How would you add a 'no two adjacent digits equal' constraint?\n"
        "• What does the 'tight' flag actually prevent from being over-counted?\n"
        "• Can you extend this to count numbers with a specific digit sum?"
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
