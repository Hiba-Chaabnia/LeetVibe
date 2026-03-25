from __future__ import annotations

TOPIC: dict = {
    "title": "Manacher's Algorithm",
    "slug": "Manacher",
    "recognize": (
        "longest palindromic substring in O(n),\n"
        "count all palindromic substrings in O(n),\n"
        "any problem needing all palindrome radii at once."
    ),
    "diagram": (
        "  Transform: insert '#' between chars to unify odd/even\n"
        "  s = abba  →  T = #a#b#b#a#\n"
        "                       0 1 2 3 4 5 6 7 8\n"
        "\n"
        "  p[i] = palindrome radius at T[i]:\n"
        "  T:  # a # b # b # a #\n"
        "  p:  0 1 0 1 4 1 0 1 0\n"
        "              ↑\n"
        "          p[4]=4 means T[0..8] is palindrome = abba\n"
        "\n"
        "  C = center of rightmost palindrome; R = its right boundary\n"
        "  For i inside [C-p[C], R]: p[i] >= min(p[mirror], R-i)\n"
        "  Then expand and update C,R if needed  →  amortised O(n)"
    ),
    "when": (
        "When you need the longest (or all) palindromic substrings in O(n).\n"
        "For a single query, expand-around-center (O(n²)) is simpler;\n"
        "use Manacher's when O(n) is required or all radii are needed."
    ),
    "patterns": [
        {
            "name": "Manacher's Algorithm — O(n) palindrome radii",
            "code": (
                "def manacher(s):\n"
                "    # Transform: insert sentinels and '#' separators\n"
                "    T = '#' + '#'.join(s) + '#'\n"
                "    n = len(T)\n"
                "    p = [0] * n     # p[i] = palindrome radius at T[i]\n"
                "    C = R = 0       # center and right boundary of rightmost palindrome\n"
                "\n"
                "    for i in range(n):\n"
                "        mirror = 2 * C - i          # mirror of i around C\n"
                "        if i < R:\n"
                "            p[i] = min(R - i, p[mirror])   # use precomputed info\n"
                "        # Attempt to expand beyond known boundary\n"
                "        while (i + p[i] + 1 < n and i - p[i] - 1 >= 0\n"
                "               and T[i + p[i] + 1] == T[i - p[i] - 1]):\n"
                "            p[i] += 1\n"
                "        # Update rightmost palindrome\n"
                "        if i + p[i] > R:\n"
                "            C, R = i, i + p[i]\n"
                "    return p\n"
                "\n"
                "def longest_palindrome(s):\n"
                "    p    = manacher(s)\n"
                "    T    = '#' + '#'.join(s) + '#'\n"
                "    best = max(range(len(T)), key=lambda i: p[i])\n"
                "    start = (best - p[best]) // 2\n"
                "    return s[start: start + p[best]]"
            ),
        },
        {
            "name": "Count all palindromic substrings in O(n)",
            "code": (
                "def count_palindromes(s):\n"
                "    p = manacher(s)\n"
                "    T = '#' + '#'.join(s) + '#'\n"
                "    # Each p[i] in the transformed string contributes (p[i]+1)//2 palindromes\n"
                "    return sum((p[i] + 1) // 2 for i in range(len(T)))\n"
                "\n"
                "# Shortest Palindrome (prepend minimum chars to make s a palindrome)\n"
                "# Equivalent to: find the longest palindromic prefix of s\n"
                "def shortest_palindrome(s):\n"
                "    p    = manacher(s)\n"
                "    T    = '#' + '#'.join(s) + '#'\n"
                "    # Find largest i such that the palindrome centered at i includes T[0]\n"
                "    best_len = 0\n"
                "    for i in range(len(T)):\n"
                "        if i - p[i] == 0:            # palindrome reaches the start\n"
                "            best_len = max(best_len, p[i])\n"
                "    return s[best_len:][::-1] + s   # prepend reverse of suffix"
            ),
        },
    ],
    "pitfalls": (
        "• The transformed string T has length 2n+1 (not 2n) — '#' is inserted\n"
        "  BETWEEN characters AND at both ends.\n"
        "• p[i] in T corresponds to a palindrome of length p[i] in the original s\n"
        "  (the '#' separators cancel out in radius → length conversion).\n"
        "• C and R track the rightmost palindrome's CENTER and RIGHT BOUNDARY,\n"
        "  not its leftmost extent — common source of off-by-one errors.\n"
        "• For most interview problems, expand-around-center (O(n²)) is acceptable;\n"
        "  only reach for Manacher's when n > 10⁵ or explicit O(n) is required."
    ),
    "time": "O(n)",
    "space": "O(n)  transformed string + radii array",
    "problems": [
        ("Longest Palindromic Substring", "M"),
        ("Palindromic Substrings",         "M"),
        ("Shortest Palindrome",            "H"),
        ("Minimum Insertions for Palindrome", "H"),
    ],
    "related": ["String Manipulation", "Z-Algorithm", "Rabin-Karp"],
}
