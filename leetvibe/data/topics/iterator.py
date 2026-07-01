from __future__ import annotations

TOPIC: dict = {
    "title": "Iterator Design Pattern",
    "slug": "Iterator",
    "recognize": (
        "Implement next() / hasNext(), flatten nested structures, peek without consuming, lazy evaluation.\n"
        "Signal: 'design a class that traverses X on demand' — the iterator pattern."
    ),
    "intuition": (
        "• Peek-and-cache: consume one element from the underlying iterator and store it — lookahead without side effects.\n"
        "• Nested iterator: a stack replaces recursion; push children in reverse so the first child is on top.\n"
        "• BST iterator: only the leftmost path lives on the stack (O(h) space, O(1) amortised per next())."
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
                "            yield from flatten(item)\n"
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
                "        self._push_left(node.right)\n"
                "        return node.val\n"
                "\n"
                "    def hasNext(self):\n"
                "        return bool(self.stack)"
            ),
        },
    ],
    "variants": (
        "• Peek Iterator — cache one element with a boolean flag; wraps any iterator.\n"
        "• Flatten Nested List — stack-based; push in reverse order; hasNext() unwinds lists until an integer is on top.\n"
        "• BST Iterator — stack holds leftmost path; _push_left on right subtree after each pop; O(h) space, O(1) amortised.\n"
        "• Flatten 2D Vector — track outer and inner indices; advance outer when inner is exhausted.\n"
        "• Zigzag Iterator — alternate between two iterators; generalises to k with round-robin index.\n"
        "• Generator-based — yield / yield from for recursive flattening; not usable when a class interface is required."
    ),
    "pitfalls": (
        "• Peek Iterator: cache with a flag — calling next() twice without a peek flag skips elements.\n"
        "• Flatten Nested List: push children in REVERSE so the first child ends up on top.\n"
        "• BST Iterator: _push_left is O(h) per call but O(1) amortised — each node pushed/popped exactly once.\n"
        "• yield from is the Pythonic recursive delegation; don't yield each item individually."
    ),
    "edge_cases": (
        "• Empty iterator — hasNext() returns False immediately; next() raises StopIteration.\n"
        "• Deeply nested empty lists — hasNext() must fully unwind all empty lists before returning False.\n"
        "• BST with only left children (linked-list shape) — stack grows to O(n); O(h) = O(n) in the worst case.\n"
        "• Peek called multiple times without next() — must return same cached value each time."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                           │\n"
        "├─────────────────────┼───────────────────────────────────────────────────┤\n"
        "│ Stack-based DFS     │ Traversal for reachability/ordering? → DFS.       │\n"
        "│                     │ On-demand sequential access via next()/hasNext()? │\n"
        "│                     │ → Iterator (may use a stack internally).          │\n"
        "├─────────────────────┼───────────────────────────────────────────────────┤\n"
        "│ Queue / deque       │ FIFO order? → Queue.                              │\n"
        "│                     │ Lazy evaluation with peek? → Iterator.            │\n"
        "└─────────────────────┴───────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Your BST Iterator uses O(h) space — can you do O(1)?\n"
        "• How would you implement a Zigzag Iterator for k lists instead of 2?\n"
        "• Can you make NestedIterator support push_back (un-consume an element)?"
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
