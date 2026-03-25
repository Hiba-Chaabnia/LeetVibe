from __future__ import annotations

TOPIC: dict = {
    "title": "Z-Algorithm",
    "slug": "Z-Algorithm",
    "recognize": (
        "pattern matching in O(n+m), find all occurrences of pattern in text,\n"
        "shortest period of string, minimum rotation,\n"
        "alternative to KMP with simpler intuition."
    ),
    "diagram": (
        "  s = aabxaaabxaab\n"
        "  Z: [-, 1, 0, 0, 3, 1, 2, 0, 0, 3, 1, 2]\n"
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
    "when": (
        "String pattern matching or period/rotation problems where\n"
        "prefix-matching length at each position is useful.\n"
        "Simpler to derive than KMP; equally powerful."
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
                "    for p in range(1, n + 1):\n"
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
    "pitfalls": (
        "• The separator character (e.g. '$') must NOT appear in pattern or text;\n"
        "  otherwise a Z value could span the boundary and give a false positive.\n"
        "• z[0] is typically set to n (whole string matches itself); some problems\n"
        "  leave it as 0 — be consistent with your definition.\n"
        "• The window [l, r] represents the Z-box with the rightmost right endpoint,\n"
        "  not just any previously computed box — updating it correctly is critical."
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
