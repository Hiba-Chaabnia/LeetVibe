from __future__ import annotations

TOPIC: dict = {
    "title": "Tries",
    "slug": "Trie",
    "recognize": (
        "prefix search, autocomplete, starts with, spell-checking,\n"
        "word search in a board, grouping words by shared prefix."
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
    "when": (
        "Prefix search, autocomplete, spell-checking,\n"
        "or grouping words by shared prefixes."
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
    "pitfalls": (
        "• search() requires is_end=True; starts_with() does not.\n"
        "• For wildcard '.', DFS over all children at that character position.\n"
        "• Array[26] instead of dict is faster but only works for lowercase a-z.\n"
        "• count field must be incremented for EVERY node along the path, not\n"
        "  just the terminal node — decrement on delete the same way."
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
