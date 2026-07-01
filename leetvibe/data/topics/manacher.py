from __future__ import annotations

TOPIC: dict = {
    "title": "Manacher's Algorithm",
    "slug": "Manacher",
    "recognize": (
        "Longest palindromic substring in O(n), count all palindromic substrings in O(n).\n"
        "Use expand-around-center (O(n²)) unless n > 10⁵ or O(n) is explicitly required."
    ),
    "intuition": (
        "• Insert '#' between characters so every palindrome has a single integer center — odd and even are unified.\n"
        "• Reuse prior radii: if i falls inside the rightmost known palindrome, p[i] ≥ min(p[mirror], R−i) — start from there.\n"
        "• R only moves right — each expansion step advances R by 1, so total work is O(n) amortised."
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
    "patterns": [
        {
            "name": "Manacher's Algorithm — O(n) palindrome radii",
            "code": (
                "def manacher(s):\n"
                "    T = '#' + '#'.join(s) + '#'\n"
                "    n = len(T)\n"
                "    p = [0] * n\n"
                "    C = R = 0\n"
                "\n"
                "    for i in range(n):\n"
                "        mirror = 2 * C - i\n"
                "        if i < R:\n"
                "            p[i] = min(R - i, p[mirror])\n"
                "        while (i + p[i] + 1 < n and i - p[i] - 1 >= 0\n"
                "               and T[i + p[i] + 1] == T[i - p[i] - 1]):\n"
                "            p[i] += 1\n"
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
            "name": "Count all palindromic substrings + Shortest Palindrome",
            "code": (
                "def count_palindromes(s):\n"
                "    p = manacher(s)\n"
                "    return sum((p[i] + 1) // 2 for i in range(len('#' + '#'.join(s) + '#')))\n"
                "\n"
                "# Shortest Palindrome — find longest palindromic prefix\n"
                "def shortest_palindrome(s):\n"
                "    p    = manacher(s)\n"
                "    T    = '#' + '#'.join(s) + '#'\n"
                "    best_len = 0\n"
                "    for i in range(len(T)):\n"
                "        if i - p[i] == 0:\n"
                "            best_len = max(best_len, p[i])\n"
                "    return s[best_len:][::-1] + s"
            ),
        },
    ],
    "variants": (
        "• Longest palindromic substring — find max p[i]; start = (best - p[best]) // 2.\n"
        "• Count all palindromic substrings — sum (p[i]+1)//2 over all i in T.\n"
        "• Shortest palindrome (prepend) — find longest palindromic prefix (condition: i - p[i] == 0).\n"
        "• Expand-around-center (simpler O(n²) alternative) — for each center expand while chars match; no transformation."
    ),
    "pitfalls": (
        "• T has length 2n+1: '#' inserted BETWEEN characters AND at both ends.\n"
        "• p[i] in T equals the palindrome length in the original s (# separators cancel out).\n"
        "• C and R track the rightmost palindrome's CENTER and RIGHT BOUNDARY — not its left extent.\n"
        "• For most interviews: expand-around-center is simpler; reach for Manacher's only when O(n) is required."
    ),
    "edge_cases": (
        "• Empty string — T = '#'; p = [0]; return ''.\n"
        "• All identical characters ('aaa') — p grows to max at center; count = n*(n+1)//2.\n"
        "• Even-length palindrome ('abba') — center lands on a '#' in T; start formula still correct.\n"
        "• Single character — T = '#a#'; p = [0,1,0]; longest palindrome is 'a'."
    ),
    "confusion": (
        "┌──────────────────────────┬───────────────────────────────────────────────────┐\n"
        "│ Often confused with      │ Distinguishing question                           │\n"
        "├──────────────────────────┼───────────────────────────────────────────────────┤\n"
        "│ Expand-around-center     │ O(n²) acceptable (n ≤ ~10⁴)? → Expand-around-     │\n"
        "│                          │ center (far simpler code).                        │\n"
        "│                          │ O(n) required or all radii needed at once?        │\n"
        "│                          │ → Manacher's.                                     │\n"
        "├──────────────────────────┼───────────────────────────────────────────────────┤\n"
        "│ DP palindrome (2D table) │ Need is-palindrome lookups for arbitrary (i,j)    │\n"
        "│                          │ inside another DP? → 2D DP table, O(n²).          │\n"
        "│                          │ Need the longest/count of palindromes?            │\n"
        "│                          │ → Manacher's, O(n).                               │\n"
        "└──────────────────────────┴───────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why is the min(p[mirror], R-i) initialisation correct?\n"
        "• Why insert '#' at both ends AND between characters?\n"
        "• For an interview, would you code Manacher's or expand-around-center?"
    ),
    "time": "O(n)",
    "space": "O(n)  transformed string + radii array",
    "problems": [
        ("Longest Palindromic Substring", "M"),
        ("Palindromic Substrings",         "M"),
        ("Shortest Palindrome",            "H"),
        ("Max Product of Two Palindromic Substrings", "H"),
    ],
    "related": ["String Manipulation", "Z-Algorithm", "Rabin-Karp"],
}
