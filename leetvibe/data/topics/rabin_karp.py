from __future__ import annotations

TOPIC: dict = {
    "title": "Rabin-Karp",
    "slug": "Rabin-Karp",
    "recognize": (
        "Substring / pattern search needing O(n+m), multi-pattern search,\n"
        "repeated DNA sequences, longest duplicate substring, rolling hash over a window.\n"
        "Signal: you need to compare many substrings of fixed length efficiently."
    ),
    "intuition": (
        "• Naïve search re-hashes from scratch at every position: O(nm). Rolling hash\n"
        "  removes the old character and adds the new one in O(1) — O(n) total.\n"
        "• Hash match → verify character-by-character. Never skip verification:\n"
        "  collisions cause false positives and wrong answers.\n"
        "• Use a large prime MOD (10⁹+7) or double-hash to keep collisions negligible."
    ),
    "diagram": (
        "  Rolling hash — slide a window of length m over text of length n:\n"
        "\n"
        "  text:    a  b  r  a  c  a  d  a  b  r  a\n"
        "  window:  [a  b  r]  →  [b  r  a]  →  [r  a  c] ...\n"
        "\n"
        "  hash(new window) = (hash(old) - old_char × base^(m-1)) × base + new_char\n"
        "                   = O(1) per slide (rolling update)\n"
        "\n"
        "  On hash match → verify character-by-character (avoid false positives)\n"
        "  Expected O(n + m)   /   Worst case O(nm) if many hash collisions"
    ),
    "patterns": [
        {
            "name": "Rabin-Karp single pattern search",
            "code": (
                "def rabin_karp(text, pattern):\n"
                "    n, m  = len(text), len(pattern)\n"
                "    BASE  = 31\n"
                "    MOD   = 10**9 + 7\n"
                "\n"
                "    # Precompute BASE^(m-1) mod MOD\n"
                "    power = pow(BASE, m - 1, MOD)\n"
                "\n"
                "    def char_val(c): return ord(c) - ord('a') + 1\n"
                "\n"
                "    # Hash of pattern\n"
                "    pat_hash = 0\n"
                "    for c in pattern:\n"
                "        pat_hash = (pat_hash * BASE + char_val(c)) % MOD\n"
                "\n"
                "    # Rolling hash over text\n"
                "    win_hash = 0\n"
                "    results  = []\n"
                "    for i, c in enumerate(text):\n"
                "        win_hash = (win_hash * BASE + char_val(c)) % MOD\n"
                "        if i >= m:                                  # slide: remove leftmost char\n"
                "            win_hash = (win_hash - char_val(text[i - m]) * power * BASE) % MOD\n"
                "        if i >= m - 1 and win_hash == pat_hash:    # hash match\n"
                "            if text[i - m + 1: i + 1] == pattern:  # verify (avoid collision)\n"
                "                results.append(i - m + 1)\n"
                "    return results"
            ),
        },
        {
            "name": "Repeated DNA Sequences — find all 10-letter substrings that appear > once",
            "code": (
                "from collections import defaultdict\n"
                "\n"
                "def find_repeated_dna(s):\n"
                "    BASE, MOD = 4, 10**9 + 7\n"
                "    encode    = {'A': 1, 'C': 2, 'G': 3, 'T': 4}\n"
                "    power     = pow(BASE, 9, MOD)   # BASE^(10-1)\n"
                "\n"
                "    seen, result = defaultdict(int), []\n"
                "    h = 0\n"
                "    for i, c in enumerate(s):\n"
                "        h = (h * BASE + encode[c]) % MOD\n"
                "        if i >= 10:\n"
                "            h = (h - encode[s[i - 10]] * BASE * power) % MOD\n"
                "        if i >= 9:\n"
                "            key = (h, s[i - 9: i + 1])  # include string to avoid collisions\n"
                "            seen[key] += 1\n"
                "            if seen[key] == 2:\n"
                "                result.append(s[i - 9: i + 1])\n"
                "    return result\n"
                "\n"
                "# Longest Duplicate Substring — binary search on length + rolling hash\n"
                "# Binary search: is there a duplicate of length mid?\n"
                "# Rolling hash: O(n) check for each candidate length\n"
                "# Combined: O(n log n)"
            ),
        },
    ],
    "variants": (
        "• Single pattern — rolling hash O(n+m) expected; verify on match.\n"
        "• Multi-pattern — store all pattern hashes in a set; O(1) membership check per window.\n"
        "• Longest duplicate substring — binary search on length + rolling hash; O(n log n).\n"
        "• Repeated DNA (fixed window=10) — hash + substring key to prevent collisions.\n"
        "• Double hashing — two independent (BASE, MOD) pairs; collision prob ≈ 1/MOD²."
    ),
    "pitfalls": (
        "• Always verify on hash match — skipping verification gives wrong answers on collisions.\n"
        "• Rolling-update off-by-one: subtract old_char × BASE^m when you add the new char first\n"
        "  (as the code above does), or old_char × BASE^(m-1) before multiplying — don't mix them.\n"
        "• Python s.find(p) is optimised internally — only implement rolling hash when required."
    ),
    "edge_cases": (
        "• Pattern longer than text — no window fits; return [] immediately.\n"
        "• All characters identical — every window matches hash; verification confirms each one.\n"
        "• Empty pattern — guard: if not pattern, return []."
    ),
    "confusion": (
        "┌──────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with  │ Distinguishing question                             │\n"
        "├──────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ KMP / Z-Algorithm    │ O(n+m) worst-case single pattern? → KMP/Z-algo.     │\n"
        "│                      │ Multi-pattern or duplicate-substring? → Rabin-Karp. │\n"
        "├──────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Sliding Window + set │ Anagram / char-frequency window? → Sliding Window.  │\n"
        "│                      │ Exact repeated substrings by hash? → Rabin-Karp.    │\n"
        "└──────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why do you need to verify after a hash match?\n"
        "• What is double hashing and when should you use it?\n"
        "• How does binary search + rolling hash find the longest duplicate substring?"
    ),
    "time": "O(n + m) expected  /  O(nm) worst case",
    "space": "O(1)  rolling hash  /  O(n) if storing all hashes",
    "problems": [
        ("Repeated DNA Sequences",          "M"),
        ("Longest Duplicate Substring",     "H"),
        ("Longest Repeating Substring",     "M"),
    ],
    "related": ["String Manipulation", "Sliding Window", "Binary Search", "Z-Algorithm"],
}
