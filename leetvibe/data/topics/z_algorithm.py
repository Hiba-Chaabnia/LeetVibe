from __future__ import annotations

TOPIC: dict = {
    "title": "Z-Algorithm",
    "slug": "Z-Algorithm",
    "recognize": (
        "Pattern matching in O(n+m), find all occurrences of pattern in text, shortest period\n"
        "of string, minimum rotation, alternative to KMP with simpler intuition.\n"
        "Keywords: prefix-match length at every position, guaranteed O(n+m), no hashing collisions."
    ),
    "intuition": (
        "• Z[i] answers one question directly: how far does s[i:] agree with s itself from the start?\n"
        "  That single array answers pattern matching (does the pattern's length appear as a Z-value\n"
        "  right after a separator) and period-finding (does the string 'restart' at position p) alike.\n"
        "• The [l, r] window caches the rightmost Z-box already proven to match a prefix — inside it,\n"
        "  Z[i] can be bootstrapped from Z[i-l] instead of re-comparing characters from scratch.\n"
        "• This is the same 'reuse prior comparisons' idea as KMP's failure function, just anchored\n"
        "  to matches against the STRING'S OWN PREFIX instead of the pattern's own prefixes/suffixes."
    ),
    "diagram": (
        "  s = aabxaaabxaab\n"
        "  Z: [-, 1, 0, 0, 2, 6, 1, 0, 0, 3, 1, 0]\n"
        "  Z[i] = length of longest substring starting at s[i]\n"
        "         that matches a PREFIX of s\n"
        "\n"
        "  Pattern matching: concatenate as  pattern + '$' + text\n"
        "  s = aab$aabxaaabxaab\n"
        "  Z[i] == len(pattern) → match at text position i - len(pattern) - 1\n"
        "\n"
        "  Window [l, r]: rightmost Z-box already computed\n"
        "  If i is inside [l,r]: Z[i] >= min(Z[i-l], r-i+1) → O(1) skip"
    ),
    "patterns": [
        {
            "name": "Build Z-array in O(n)",
            "code": (
                "def z_function(s):\n"
                "    n = len(s)\n"
                "    z = [0] * n\n"
                "    z[0] = n          # by convention, or left as 0\n"
                "    l = r = 0         # [l, r] is the rightmost Z-box\n"
                "    for i in range(1, n):\n"
                "        if i < r:\n"
                "            z[i] = min(r - i, z[i - l])   # use previously computed info\n"
                "        while i + z[i] < n and s[z[i]] == s[i + z[i]]:\n"
                "            z[i] += 1                      # naive extend\n"
                "        if i + z[i] > r:\n"
                "            l, r = i, i + z[i]             # update rightmost Z-box\n"
                "    return z\n"
                "\n"
                "# Pattern search using Z-algorithm\n"
                "def z_search(text, pattern):\n"
                "    combined = pattern + '$' + text       # '$' can't appear in pattern\n"
                "    z = z_function(combined)\n"
                "    m = len(pattern)\n"
                "    return [i - m - 1                     # convert back to text index\n"
                "            for i in range(m + 1, len(combined))\n"
                "            if z[i] == m]"
            ),
        },
        {
            "name": "Shortest period of a string using Z-array",
            "code": (
                "# Period p: s[i] == s[i % p] for all i\n"
                "# Smallest p such that (n % p == 0) and z[p] == n - p\n"
                "def shortest_period(s):\n"
                "    n = len(s)\n"
                "    z = z_function(s)\n"
                "    for p in range(1, n):          # p == n would index z[n] out of range\n"
                "        if n % p == 0 and z[p] == n - p:\n"
                "            return p\n"
                "    return n   # no shorter period, string is its own period\n"
                "\n"
                "# Repeated Substring Pattern (LeetCode 459)\n"
                "# A string has a repeated pattern iff shortest_period(s) < len(s)\n"
                "def repeated_substring(s):\n"
                "    return shortest_period(s) < len(s)\n"
                "\n"
                "# Z vs KMP:\n"
                "# KMP  → failure function; think 'how far back to fall when mismatch'\n"
                "# Z    → Z-array;         think 'how long is the prefix match at each i'\n"
                "# Both O(n+m); Z is arguably simpler to implement from scratch."
            ),
        },
    ],
    "variants": (
        "• Pattern search — concatenate pattern + '$' + text; Z[i] == len(pattern) marks a match.\n"
        "• Shortest period — smallest p where n % p == 0 and Z[p] == n - p.\n"
        "• Repeated Substring Pattern — string has a repeating unit iff shortest_period(s) < len(s).\n"
        "• Longest Happy Prefix — the longest prefix that's also a suffix; read off the Z-array\n"
        "  by finding the largest i + Z[i] == n.\n"
        "• Shortest palindrome via prefix-suffix trick — combine s + '#' + reverse(s), use Z or KMP\n"
        "  to find the longest prefix of s that's also a suffix of reverse(s)."
    ),
    "pitfalls": (
        "• The separator character (e.g. '$') must NOT appear in pattern or text; otherwise a Z\n"
        "  value could span the boundary and give a false positive.\n"
        "• z[0] is typically set to n (whole string matches itself); some problems leave it as 0 —\n"
        "  be consistent with your definition.\n"
        "• The window [l, r] represents the Z-box with the rightmost right endpoint, not just any\n"
        "  previously computed box — updating it correctly is critical."
    ),
    "edge_cases": (
        "• Empty pattern or text — guard before concatenating; Z-array of length 0 has no valid index.\n"
        "• Pattern longer than text — no match possible; the search loop naturally finds none.\n"
        "• Pattern equals the whole text — Z[m+1] == m, matched at index 0.\n"
        "• String with no repeating structure — shortest_period returns n (the whole string)."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Rabin-Karp          │ Need a guaranteed O(n+m) worst case with no collision │\n"
        "│                     │ risk? → Z-Algorithm/KMP.                              │\n"
        "│                     │ OK with average-case speed and want simple            │\n"
        "│                     │ multi-pattern rolling-hash matching? → Rabin-Karp.    │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How is the Z-array related to KMP's failure function — can you derive one from the other?\n"
        "• Why must the separator character not appear anywhere in pattern or text?\n"
        "• How would you find the longest prefix that's also a suffix using the Z-array?\n"
        "• Can you adapt this to find the minimum lexicographic rotation of a string?"
    ),
    "time": "O(n + m)  build + search",
    "space": "O(n + m)  Z-array of combined string",
    "problems": [
        ("Find the Index of First Occurrence", "E"),
        ("Repeated Substring Pattern",         "E"),
        ("Shortest Palindrome",                "H"),
        ("Longest Happy Prefix",               "H"),
        ("Sum of Scores of Built Strings",     "H"),
    ],
    "related": ["String Manipulation", "Rabin-Karp"],
}
