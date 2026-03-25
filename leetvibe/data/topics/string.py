from __future__ import annotations

TOPIC: dict = {
    "title": "String Manipulation",
    "slug": "String",
    "recognize": (
        "reverse words, rotate string, encode/decode,\n"
        "run-length encoding, palindrome, pattern matching,\n"
        "string parsing, find first occurrence in string."
    ),
    "diagram": (
        "  Expand-around-center (Longest Palindromic Substring):\n"
        "  s = cbabad\n"
        "  center at index 2 ('a'):\n"
        "  l=2,r=2 → 'a'          palindrome len 1\n"
        "  l=1,r=3 → 'b'=='b' ✓  palindrome len 3  'bab'\n"
        "  l=0,r=4 → 'c'!='a' ✗  stop\n"
        "  Also try even centers: l=i, r=i+1\n"
        "\n"
        "  KMP failure table (partial match table):\n"
        "  pattern: a b a b c\n"
        "  lps:     0 0 1 2 0\n"
        "  On mismatch at j, jump to lps[j-1] instead of restarting"
    ),
    "when": (
        "In-place string transforms, palindrome checking,\n"
        "encoding/decoding, word-level parsing, or O(n+m) pattern matching."
    ),
    "patterns": [
        {
            "name": "Reverse words in a string (split + rejoin)",
            "code": (
                "return ' '.join(s.split()[::-1])\n"
                "\n"
                "# Valid Palindrome — skip non-alphanumeric\n"
                "l, r = 0, len(s) - 1\n"
                "while l < r:\n"
                "    while l < r and not s[l].isalnum(): l += 1\n"
                "    while l < r and not s[r].isalnum(): r -= 1\n"
                "    if s[l].lower() != s[r].lower(): return False\n"
                "    l += 1; r -= 1\n"
                "return True\n"
                "\n"
                "# Longest Palindromic Substring — expand around center  O(n²) / O(1)\n"
                "def expand(s, l, r):\n"
                "    while l >= 0 and r < len(s) and s[l] == s[r]:\n"
                "        l -= 1; r += 1\n"
                "    return s[l + 1 : r]         # last valid palindrome\n"
                "\n"
                "res = ''\n"
                "for i in range(len(s)):\n"
                "    odd  = expand(s, i, i)      # odd-length center\n"
                "    even = expand(s, i, i + 1)  # even-length center\n"
                "    if len(odd)  > len(res): res = odd\n"
                "    if len(even) > len(res): res = even\n"
                "return res"
            ),
        },
        {
            "name": "Encode / Decode Strings — length-prefixed, delimiter-free",
            "code": (
                "def encode(strs):\n"
                "    return ''.join(f'{len(s)}#{s}' for s in strs)\n"
                "\n"
                "def decode(s):\n"
                "    res, i = [], 0\n"
                "    while i < len(s):\n"
                "        j = s.index('#', i)\n"
                "        length = int(s[i:j])\n"
                "        res.append(s[j + 1: j + 1 + length])\n"
                "        i = j + 1 + length\n"
                "    return res\n"
                "\n"
                "# KMP — find all occurrences of pattern in text  O(n + m)\n"
                "def kmp_search(text, pattern):\n"
                "    # Build failure function (longest proper prefix that is also suffix)\n"
                "    m = len(pattern)\n"
                "    lps = [0] * m\n"
                "    length, i = 0, 1\n"
                "    while i < m:\n"
                "        if pattern[i] == pattern[length]:\n"
                "            length += 1; lps[i] = length; i += 1\n"
                "        elif length:\n"
                "            length = lps[length - 1]   # fall back, don't advance i\n"
                "        else:\n"
                "            lps[i] = 0; i += 1\n"
                "\n"
                "    # Search\n"
                "    results = []\n"
                "    i = j = 0\n"
                "    while i < len(text):\n"
                "        if text[i] == pattern[j]:\n"
                "            i += 1; j += 1\n"
                "        if j == m:\n"
                "            results.append(i - j)   # match found at index i-j\n"
                "            j = lps[j - 1]\n"
                "        elif i < len(text) and text[i] != pattern[j]:\n"
                "            if j: j = lps[j - 1]\n"
                "            else: i += 1\n"
                "    return results\n"
                "# Python shortcut for single search: text.find(pattern) or 'pattern' in text"
            ),
        },
    ],
    "pitfalls": (
        "• s.split() strips leading/trailing spaces and collapses multiple spaces;\n"
        "  s.split(' ') does NOT — it creates empty strings for each space.\n"
        "• Python strings are immutable: convert to list for in-place operations.\n"
        "• Expand-around-center: try BOTH odd (l=i,r=i) and even (l=i,r=i+1) centers.\n"
        "• KMP failure table: on mismatch fall back to lps[j-1], don't reset j to 0.\n"
        "• Encode/decode: comma as delimiter breaks on strings containing commas —\n"
        "  length-prefix '4#word' is safe for any byte content."
    ),
    "time": "O(n) most ops  /  O(n²) expand-around-center  /  O(n+m) KMP",
    "space": "O(n) for output  /  O(1) in-place  /  O(m) KMP failure table",
    "problems": [
        ("Reverse Words in a String",                "M"),
        ("Longest Palindromic Substring",            "M"),
        ("Find the Index of the First Occurrence",   "E"),
        ("Repeated Substring Pattern",               "E"),
        ("String to Integer (atoi)",                 "M"),
        ("Count and Say",                            "M"),
    ],
    "related": ["Two Pointers", "Sliding Window", "Arrays & Hashing", "Z-Algorithm", "Rabin-Karp"],
}
