from __future__ import annotations

TOPIC: dict = {
    "title": "Stack",
    "slug": "Stack",
    "recognize": (
        "matching brackets, undo/redo, expression evaluation,\n"
        "  \"valid\" parentheses, iterative DFS, min-stack queries."
    ),
    "diagram": (
        "  push →  ┌───┐\n"
        "          │ 5 │  ← top (most recent)\n"
        "          ├───┤\n"
        "          │ 3 │\n"
        "          ├───┤\n"
        "          │ 1 │\n"
        "          └───┘\n"
        "  pop  →  removes top   (LIFO)\n"
        "\n"
        "  stack.append(x)  — push\n"
        "  stack.pop()      — pop\n"
        "  stack[-1]        — peek (no pop)"
    ),
    "when": (
        "Matching brackets, undo/redo, next-greater-element,\n"
        "  expression evaluation, or iterative DFS."
    ),
    "pattern": (
        "# Valid Parentheses\n"
        "pairs = {')': '(', ']': '[', '}': '{'}\n"
        "stack = []\n"
        "for ch in s:\n"
        "    if ch in '({[':\n"
        "        stack.append(ch)\n"
        "    elif not stack or stack[-1] != pairs[ch]:\n"
        "        return False\n"
        "    else:\n"
        "        stack.pop()\n"
        "return not stack"
    ),
    "pattern2": (
        "# Min Stack — O(1) getMin using auxiliary stack\n"
        "class MinStack:\n"
        "    def __init__(self):\n"
        "        self.stack     = []\n"
        "        self.min_stack = []\n"
        "    def push(self, val):\n"
        "        self.stack.append(val)\n"
        "        m = min(val, self.min_stack[-1] if self.min_stack else val)\n"
        "        self.min_stack.append(m)\n"
        "    def pop(self):\n"
        "        self.stack.pop(); self.min_stack.pop()\n"
        "    def getMin(self): return self.min_stack[-1]"
    ),
    "pitfalls": (
        "• Check stack is non-empty before stack[-1] or stack.pop().\n"
        "• Min Stack: push AND pop both stacks together, always.\n"
        "• Evaluate RPN: pop TWO operands — b = pop(), a = pop() (order matters)."
    ),
    "time": "O(n)",
    "space": "O(n)",
    "problems": [
        ("Valid Parentheses",                "E"),
        ("Min Stack",                        "M"),
        ("Evaluate Reverse Polish Notation", "M"),
        ("Daily Temperatures",              "M"),
        ("Largest Rectangle in Histogram",  "H"),
        ("Basic Calculator II",             "M"),
    ],
    "related": ["Monotonic Stack", "Queue", "Backtracking", "Iterator Design Pattern", "Eulerian Path / Circuit"],
}
