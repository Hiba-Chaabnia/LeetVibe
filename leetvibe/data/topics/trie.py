from __future__ import annotations

TOPIC: dict = {
    "title": "Tries",
    "slug": "Trie",
    "recognize": (
        "Prefix search, autocomplete, starts with, spell-checking, word search in a board,\n"
        "grouping words by shared prefix.\n"
        "Keywords: repeated PREFIX operations across many words, not just exact-match lookup."
    ),
    "intuition": (
        "• Words sharing a prefix share the same path from the root — storing that path once instead\n"
        "  of once per word is what makes prefix queries O(m) regardless of how many words are stored.\n"
        "• A hash set can only answer 'is this exact string present' in O(1) — it has no notion of\n"
        "  'characters so far', so prefix/autocomplete queries would need scanning every entry.\n"
        "• is_end marks completed words distinctly from intermediate prefixes, so 'cat' being stored\n"
        "  doesn't make 'ca' incorrectly register as a valid word."
    ),
    "diagram": (
        '  insert: "car"  "cat"  "cab"\n'
        "\n"
        "       root\n"
        "        |\n"
        "        c\n"
        "        |\n"
        "        a\n"
        "       /|\\\n"
        "      r  t  b\n"
        "      *  *  *    (* = is_end)\n"
        "\n"
        '  search("cat") → root→c→a→t → found (is_end=True)\n'
        '  startsWith("ca") → root→c→a → True (no is_end check)'
    ),
    "patterns": [
        {
            "name": "Trie Implementation",
            "code": (
                "class TrieNode:\n"
                "    def __init__(self):\n"
                "        self.children = {}\n"
                "        self.is_end   = False\n"
                "        self.count    = 0     # how many words pass through this node\n"
                "\n"
                "class Trie:\n"
                "    def __init__(self): self.root = TrieNode()\n"
                "\n"
                "    def insert(self, word):\n"
                "        node = self.root\n"
                "        for ch in word:\n"
                "            node = node.children.setdefault(ch, TrieNode())\n"
                "            node.count += 1   # increment prefix frequency\n"
                "        node.is_end = True\n"
                "\n"
                "    def search(self, word):\n"
                "        node = self.root\n"
                "        for ch in word:\n"
                "            if ch not in node.children: return False\n"
                "            node = node.children[ch]\n"
                "        return node.is_end\n"
                "\n"
                "    def starts_with(self, prefix):\n"
                "        node = self.root\n"
                "        for ch in prefix:\n"
                "            if ch not in node.children: return False\n"
                "            node = node.children[ch]\n"
                "        return True\n"
                "\n"
                "    def count_prefix(self, prefix):\n"
                "        node = self.root\n"
                "        for ch in prefix:\n"
                "            if ch not in node.children: return 0\n"
                "            node = node.children[ch]\n"
                "        return node.count   # number of words with this prefix"
            ),
        },
        {
            "name": "Wildcard search with '.' — DFS over all children at dot position",
            "code": (
                "class WordDictionary:\n"
                "    def __init__(self):\n"
                "        self.root = TrieNode()\n"
                "\n"
                "    def add_word(self, word):\n"
                "        node = self.root\n"
                "        for ch in word:\n"
                "            node = node.children.setdefault(ch, TrieNode())\n"
                "        node.is_end = True\n"
                "\n"
                "    def search(self, word):\n"
                "        def dfs(node, i):\n"
                "            if i == len(word): return node.is_end\n"
                "            ch = word[i]\n"
                "            if ch == '.':\n"
                "                return any(dfs(child, i + 1)\n"
                "                           for child in node.children.values())\n"
                "            if ch not in node.children: return False\n"
                "            return dfs(node.children[ch], i + 1)\n"
                "        return dfs(self.root, 0)"
            ),
        },
    ],
    "variants": (
        "• Standard Trie — insert/search/startsWith; array[26] children for speed if lowercase a-z only.\n"
        "• Prefix count Trie — increment a counter at every node along the insert path.\n"
        "• Wildcard search ('.') — DFS branches over all children at the wildcard position.\n"
        "• Word Search II (board + word list) — Trie prunes DFS paths that can't match any word.\n"
        "• Compressed Trie (radix tree) — merge single-child chains into one edge to save space."
    ),
    "pitfalls": (
        "• search() requires is_end=True; starts_with() does not.\n"
        "• For wildcard '.', DFS over all children at that character position.\n"
        "• Array[26] instead of dict is faster but only works for lowercase a-z.\n"
        "• count field must be incremented for EVERY node along the path, not just the terminal\n"
        "  node — decrement on delete the same way."
    ),
    "edge_cases": (
        "• Empty string insert/search — decide whether root.is_end=True counts as containing '',\n"
        "  most implementations treat it as valid.\n"
        "• Single character words — is_end set on the first-level child.\n"
        "• Word that's a prefix of another (e.g. 'car' and 'card') — is_end distinguishes them\n"
        "  correctly at their respective nodes.\n"
        "• All wildcard query ('...') — DFS branches at every position; worst case O(26^m)."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Arrays & Hashing    │ Only need exact-match membership (is this word       │\n"
        "│ (hash set)          │ present)? → Hash Set, O(1). Need PREFIX operations   │\n"
        "│                     │ (startsWith, autocomplete, count words with prefix)? │\n"
        "│                     │ → Trie.                                              │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How would you support wildcard '.' search efficiently for many queries?\n"
        "• Can you reduce memory usage for a Trie with many long, sparse words?\n"
        "• How would you return the top-k autocomplete suggestions for a prefix?\n"
        "• Word Search II: how does the Trie let you prune the board DFS early?"
    ),
    "time": "O(m)  per insert/search  (m = word length)",
    "space": "O(m × n)  n = number of words",
    "problems": [
        ("Implement Trie",                            "M"),
        ("Design Add and Search Words Data Structure","M"),
        ("Longest Common Prefix",                     "E"),
        ("Replace Words",                             "M"),
        ("Word Search II",                            "H"),
    ],
    "related": ["Backtracking", "Arrays & Hashing"],
}
