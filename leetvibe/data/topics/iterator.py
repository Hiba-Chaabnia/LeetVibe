from __future__ import annotations

TOPIC: dict = {
    "title": "Iterator Design Pattern",
    "slug": "Iterator",
    "recognize": (
        "implement next() / hasNext(), flatten nested structures,\n"
        "peek at the next element without consuming it,\n"
        "lazy evaluation of a sequence, generator-based traversal."
    ),
    "diagram": (
        "  Iterator contract:\n"
        "  __iter__(self) → returns self\n"
        "  __next__(self) → returns next value, raises StopIteration when done\n"
        "\n"
        "  Peek Iterator wraps any iterator:\n"
        "  [1, 2, 3, 4]  →  peek() = 1 (no advance)  →  next() = 1  →  peek() = 2\n"
        "\n"
        "  Flatten Nested List: [1, [4, [6]]] → 1, 4, 6\n"
        "  Use a stack; push children in reverse order for correct traversal\n"
        "\n"
        "  Generator shortcut: yield from flattens any iterable lazily"
    ),
    "when": (
        "Design problems requiring lazy sequential access to a data source.\n"
        "Any time you need next() / hasNext() semantics, or must flatten\n"
        "a recursive/nested structure into a flat stream."
    ),
    "patterns": [
        {
            "name": "Peek Iterator — wraps an existing iterator, enables one-element lookahead",
            "code": (
                "class PeekingIterator:\n"
                "    def __init__(self, iterator):\n"
                "        self._iter  = iterator\n"
                "        self._peeked = False\n"
                "        self._peek_val = None\n"
                "\n"
                "    def peek(self):\n"
                "        if not self._peeked:\n"
                "            self._peek_val = next(self._iter)\n"
                "            self._peeked   = True\n"
                "        return self._peek_val\n"
                "\n"
                "    def next(self):\n"
                "        if self._peeked:\n"
                "            self._peeked = False\n"
                "            return self._peek_val\n"
                "        return next(self._iter)\n"
                "\n"
                "    def hasNext(self):\n"
                "        try:\n"
                "            self.peek()\n"
                "            return True\n"
                "        except StopIteration:\n"
                "            return False"
            ),
        },
        {
            "name": "Flatten Nested List Iterator — stack-based",
            "code": (
                "class NestedIterator:\n"
                "    def __init__(self, nestedList):\n"
                "        self.stack = nestedList[::-1]   # reversed so top = first element\n"
                "\n"
                "    def next(self):\n"
                "        return self.stack.pop().getInteger()\n"
                "\n"
                "    def hasNext(self):\n"
                "        while self.stack:\n"
                "            top = self.stack[-1]\n"
                "            if top.isInteger(): return True\n"
                "            self.stack.pop()\n"
                "            self.stack.extend(reversed(top.getList()))\n"
                "        return False\n"
                "\n"
                "# Python Generator approach — cleaner for simple flattening\n"
                "def flatten(nested):\n"
                "    for item in nested:\n"
                "        if isinstance(item, list):\n"
                "            yield from flatten(item)   # recursive generator\n"
                "        else:\n"
                "            yield item\n"
                "\n"
                "# BST Iterator — inorder traversal on demand (O(h) space)\n"
                "class BSTIterator:\n"
                "    def __init__(self, root):\n"
                "        self.stack = []\n"
                "        self._push_left(root)\n"
                "\n"
                "    def _push_left(self, node):\n"
                "        while node:\n"
                "            self.stack.append(node)\n"
                "            node = node.left\n"
                "\n"
                "    def next(self):\n"
                "        node = self.stack.pop()\n"
                "        self._push_left(node.right)   # prepare right subtree\n"
                "        return node.val\n"
                "\n"
                "    def hasNext(self):\n"
                "        return bool(self.stack)"
            ),
        },
    ],
    "pitfalls": (
        "• Peek Iterator: cache the peeked value with a flag — don't call next()\n"
        "  twice or you'll skip elements.\n"
        "• Flatten Nested List: push children in REVERSE order onto the stack\n"
        "  so the first child ends up on top.\n"
        "• BST Iterator: the _push_left helper maintains O(h) stack space —\n"
        "  the amortised cost of next() is O(1), not O(h) per call.\n"
        "• yield from is the Pythonic way to delegate to sub-generators;\n"
        "  don't manually loop and yield each item when flattening."
    ),
    "time": "O(1) amortised next() / hasNext()",
    "space": "O(h) BST iterator (h = tree height)  /  O(d) nested list (d = depth)",
    "problems": [
        ("Peeking Iterator",              "M"),
        ("Flatten Nested List Iterator",  "M"),
        ("Binary Search Tree Iterator",   "M"),
        ("Flatten 2D Vector",             "M"),
        ("Zigzag Iterator",               "M"),
        ("Design Compressed String Iter", "M"),
    ],
    "related": ["Stack", "Trees", "Backtracking"],
}
