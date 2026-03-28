from __future__ import annotations

TOPIC: dict = {
    "title": "Stack",
    "slug": "Stack",
    "recognize": (
        "Matching brackets, undo/redo, expression evaluation, valid parentheses,\n"
        "iterative DFS, min-stack queries.\n"
        "Keywords: LIFO order matters, most-recently-seen item is processed first, nested structure."
    ),
    "intuition": (
        "• A stack mirrors nesting: the last thing opened must be the first thing closed — exactly\n"
        "  the structure of brackets, function calls, and recursive DFS.\n"
        "• Pushing state before recursing (and popping after) turns recursion into an explicit loop,\n"
        "  which is why a stack replaces the call stack for iterative DFS.\n"
        "• An auxiliary stack (Min Stack) trades O(n) space for O(1) query time by caching, at each\n"
        "  push, the answer as-of-that-point — so popping just rewinds to the previously cached answer."
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
    "patterns": [
        {
            "name": "Valid Parentheses",
            "code": (
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
        },
        {
            "name": "Min Stack — O(1) getMin using auxiliary stack",
            "code": (
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
        },
    ],
    "variants": (
        "• Bracket matching (Valid Parentheses) — push opens, pop-and-compare on close.\n"
        "• Auxiliary min/max stack — parallel stack caches the running extreme at each push.\n"
        "• Expression evaluation (RPN, Basic Calculator) — operands and operators both live on stacks.\n"
        "• Next-greater/smaller-element — see Monotonic Stack for the O(n) specialised variant.\n"
        "• Iterative DFS — explicit stack of (node, state) replaces the recursive call stack."
    ),
    "pitfalls": (
        "• Check stack is non-empty before stack[-1] or stack.pop() — empty pop raises IndexError.\n"
        "• Min Stack: push AND pop both stacks together, always, or they desync.\n"
        "• Evaluate RPN: pop TWO operands as b = pop(), a = pop() — order matters for - and /."
    ),
    "edge_cases": (
        "• Empty string (Valid Parentheses) — vacuously valid; return True.\n"
        "• Unmatched closing bracket with empty stack — must check stack non-empty before popping.\n"
        "• All opening brackets, no closing — stack never empties; return False at the end.\n"
        "• Single element (Min Stack) — getMin() returns that element; push/pop symmetric."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Monotonic Stack     │ Just need LIFO order (matching, undo, parsing)? →     │\n"
        "│                     │ plain Stack. Need 'next greater/smaller element' with │\n"
        "│                     │ elements kept in sorted order on the stack? →         │\n"
        "│                     │ Monotonic Stack.                                      │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How would you validate brackets with three types AND wildcard characters?\n"
        "• Min Stack: can you do it with O(1) space instead of a second stack?\n"
        "• How would you convert your iterative DFS back to recursive, and what's the trade-off?\n"
        "• Basic Calculator: how do you handle nested parentheses with + and - only?"
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
