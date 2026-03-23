from __future__ import annotations

TOPIC: dict = {
    "title": "Rabin-Karp",
    "slug": "Rabin-Karp",
    "recognize": (
        "substring / pattern search needing O(n+m), multi-pattern search,\n"
        "  \"repeated DNA sequences\", \"longest duplicate substring\",\n"
        "  rolling hash over a window."
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
    "when": (
        "Multi-pattern search (Aho-Corasick is stronger but complex).\n"
        "  Problems where you need to hash a substring and slide efficiently:\n"
        "  repeated substrings, longest duplicate substring, anagram detection."
    ),
    "pattern": (
        "# Rabin-Karp single pattern search\n"
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
    "pattern2": (
        "# Repeated DNA Sequences — find all 10-letter substrings that appear > once\n"
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
    "pitfalls": (
        "• Always verify on hash match — hash collisions cause false positives;\n"
        "  skipping verification gives wrong answers.\n"
        "• Rolling update: subtract the leaving character's contribution using\n"
        "  BASE^(m-1), not BASE^m — off-by-one is the most common bug.\n"
        "• Use a large prime MOD to minimise collisions; double-hashing\n"
        "  (two independent hash functions) nearly eliminates false positives.\n"
        "• Python's built-in s.find(p) uses an optimised algorithm internally —\n"
        "  only implement Rabin-Karp when the problem explicitly tests rolling hash."
    ),
    "time": "O(n + m) expected  /  O(nm) worst case",
    "space": "O(1)  rolling hash  /  O(n) if storing all hashes",
    "problems": [
        ("Repeated DNA Sequences",          "M"),
        ("Longest Duplicate Substring",     "H"),
        ("Longest Repeating Substring",     "M"),
        ("Find All Anagrams in a String",   "M"),
        ("Minimum Window Substring",        "H"),
    ],
    "related": ["String Manipulation", "Sliding Window", "Binary Search", "Z-Algorithm"],
}
