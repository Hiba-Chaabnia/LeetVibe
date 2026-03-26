from __future__ import annotations

TOPIC: dict = {
    "title": "Backtracking",
    "slug": "Backtracking",
    "recognize": (
        "All combinations, all permutations, all subsets, N-Queens, Sudoku, Word Search, Palindrome Partitioning.\n"
        "Signal: 'return all' — if the problem asks to enumerate solutions, it's almost always backtracking."
    ),
    "intuition": (
        "• Every solution is a path from root to leaf in a decision tree — build it incrementally.\n"
        "• Undo the last choice before trying the next branch (unchoose) — same path object, no copying.\n"
        "• Prune early: if a partial path already violates a constraint, skip the entire subtree."
    ),
    "diagram": (
        "  Subsets of [1, 2, 3]:\n"
        "\n"
        "               []\n"
        "             /    \\\n"
        "           [1]    []\n"
        "          /   \\   / \\\n"
        "       [1,2] [1] [2] []\n"
        "        /\n"
        "    [1,2,3]\n"
        "\n"
        "  pattern:  choose → explore → unchoose (undo)"
    ),
    "patterns": [
        {
            "name": "Subsets / Combinations",
            "code": (
                "def backtrack(start, path):\n"
                "    result.append(path[:])           # record a copy\n"
                "    for i in range(start, len(nums)):\n"
                "        path.append(nums[i])          # choose\n"
                "        backtrack(i + 1, path)        # explore\n"
                "        path.pop()                    # unchoose\n"
                "\n"
                "result = []; backtrack(0, []); return result\n"
                "\n"
                "# Letter Combinations / Generate Parentheses — build character by character\n"
                "# Key: branch on each valid next character; no 'start index' needed\n"
                "phone = {'2':'abc','3':'def','4':'ghi','5':'jkl',\n"
                "         '6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}\n"
                "\n"
                "def bt(idx, path):\n"
                "    if idx == len(digits):\n"
                "        result.append(''.join(path)); return\n"
                "    for ch in phone[digits[idx]]:\n"
                "        path.append(ch)\n"
                "        bt(idx + 1, path)\n"
                "        path.pop()\n"
                "\n"
                "result = []; bt(0, []); return result\n"
                "\n"
                "# Generate Parentheses — constraint: open <= n, close <= open\n"
                "def bt(path, open_count, close_count):\n"
                "    if len(path) == 2 * n:\n"
                "        result.append(''.join(path)); return\n"
                "    if open_count  < n:\n"
                "        path.append('('); bt(path, open_count + 1, close_count); path.pop()\n"
                "    if close_count < open_count:\n"
                "        path.append(')'); bt(path, open_count, close_count + 1); path.pop()\n"
                "\n"
                "result = []; bt([], 0, 0); return result"
            ),
        },
        {
            "name": "Permutations with duplicates — used[] array",
            "code": (
                "nums.sort()   # sort so duplicates are adjacent\n"
                "used = [False] * len(nums)\n"
                "\n"
                "def backtrack(path):\n"
                "    if len(path) == len(nums):\n"
                "        result.append(path[:]); return\n"
                "    for i in range(len(nums)):\n"
                "        if used[i]: continue\n"
                "        if i > 0 and nums[i] == nums[i-1] and not used[i-1]: continue\n"
                "        used[i] = True\n"
                "        path.append(nums[i])\n"
                "        backtrack(path)\n"
                "        path.pop()\n"
                "        used[i] = False\n"
                "\n"
                "# Constraint-satisfaction (Sudoku) — try/place/backtrack\n"
                "def solve(board):\n"
                "    empty = [(r, c) for r in range(9) for c in range(9) if board[r][c] == '.']\n"
                "    rows  = [set() for _ in range(9)]\n"
                "    cols  = [set() for _ in range(9)]\n"
                "    boxes = [set() for _ in range(9)]\n"
                "    for r in range(9):\n"
                "        for c in range(9):\n"
                "            if board[r][c] != '.':\n"
                "                d = board[r][c]\n"
                "                rows[r].add(d); cols[c].add(d); boxes[(r//3)*3+c//3].add(d)\n"
                "\n"
                "    def bt(idx):\n"
                "        if idx == len(empty): return True\n"
                "        r, c = empty[idx]\n"
                "        box  = (r // 3) * 3 + c // 3\n"
                "        for d in '123456789':\n"
                "            if d in rows[r] or d in cols[c] or d in boxes[box]: continue\n"
                "            board[r][c] = d\n"
                "            rows[r].add(d); cols[c].add(d); boxes[box].add(d)\n"
                "            if bt(idx + 1): return True\n"
                "            board[r][c] = '.'\n"
                "            rows[r].discard(d); cols[c].discard(d); boxes[box].discard(d)\n"
                "        return False\n"
                "\n"
                "    bt(0)"
            ),
        },
    ],
    "variants": (
        "• Subsets (no duplicates) — append path copy at every node; use start index.\n"
        "• Subsets II (with duplicates) — sort; skip nums[i]==nums[i-1] when i > start.\n"
        "• Combination Sum (reuse allowed) — pass i (not i+1) so the same element can repeat.\n"
        "• Combination Sum II (no reuse, duplicates) — sort + skip same value at same depth.\n"
        "• Permutations (no duplicates) — no start index; use a visited/used array.\n"
        "• Permutations II (with duplicates) — sort + skip when nums[i]==nums[i-1] and not used[i-1].\n"
        "• Constraint-satisfaction (N-Queens, Sudoku) — maintain aux sets for O(1) validity checks.\n"
        "• Word Search (grid DFS) — mark cell in-place (board[r][c]='#'); restore on backtrack."
    ),
    "pitfalls": (
        "• Append path[:] (a copy), not path — path is mutated throughout.\n"
        "• Permutations with duplicates: sort + skip same value only when prev sibling not used.\n"
        "• Sudoku: maintain row/col/box sets for O(1) validity, not O(9) board scans.\n"
        "• Python recursion limit: sys.setrecursionlimit(10**5) for deep trees."
    ),
    "edge_cases": (
        "• Empty input — backtrack never enters the loop; subsets should return [[]], not [].\n"
        "• All identical elements — without duplicate-skip logic, result has n! identical permutations.\n"
        "• target == 0 in Combination Sum — empty subset [] is valid; base case must record it.\n"
        "• Sudoku board already solved — bt(0) returns True at idx==0 without entering the loop."
    ),
    "confusion": (
        "┌───────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                              │\n"
        "├───────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Dynamic Programming   │ Do you need every solution, or just the count /      │\n"
        "│                       │ optimal value? DP counts/optimises; backtracking     │\n"
        "│                       │ enumerates. If the problem says 'return all', it's   │\n"
        "│                       │ almost always backtracking.                          │\n"
        "├───────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ DFS on a graph / tree │ Is there a fixed combinatorial structure (subsets,   │\n"
        "│                       │ permutations, placements) being built step by step,  │\n"
        "│                       │ or are you traversing an existing graph/tree? The    │\n"
        "│                       │ 'unchoose' undo step is the hallmark of backtracking │\n"
        "│                       │ and does not appear in plain DFS.                    │\n"
        "└───────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you generate the subsets iteratively instead of recursively?\n"
        "• If you only need the count of valid combinations, can you do better than backtracking?\n"
        "• How would you parallelise this?\n"
        "• Your Sudoku solver is slow on adversarial boards — how do you speed it up?"
    ),
    "time": "O(2ⁿ) subsets   /   O(n!) permutations",
    "space": "O(n)   recursion depth",
    "problems": [
        ("Subsets",                   "M"),
        ("Combination Sum",           "M"),
        ("Permutations",              "M"),
        ("Permutations II",           "M"),
        ("Letter Combinations",       "M"),
        ("Generate Parentheses",      "M"),
        ("Word Search",               "M"),
        ("Palindrome Partitioning",   "M"),
        ("N-Queens",                  "H"),
        ("Sudoku Solver",             "H"),
    ],
    "related": ["Tries", "Dynamic Programming", "Iterator Design Pattern"],
}
