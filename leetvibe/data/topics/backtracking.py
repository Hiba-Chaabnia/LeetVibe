from __future__ import annotations

TOPIC: dict = {
    "title": "Backtracking",
    "slug": "Backtracking",
    "recognize": (
        "all combinations, all permutations, all subsets,\n"
        "N-Queens, Sudoku, Word Search, Palindrome Partitioning."
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
    "when": (
        "Generating all combinations, permutations, or subsets.\n"
        "Constraint-satisfaction (N-Queens, Sudoku, Word Search)."
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
    "pitfalls": (
        "• Append path[:] (a copy), not path — path is mutated throughout.\n"
        "• Permutations with duplicates: sort + skip same value when prev not used.\n"
        "• Pruning: add early-exit conditions before recursing to cut dead branches.\n"
        "• Constraint problems (Sudoku): maintain row/col/box sets to check validity\n"
        "  in O(1) instead of scanning the board each time.\n"
        "• Python recursion limit: import sys; sys.setrecursionlimit(10**5)."
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
