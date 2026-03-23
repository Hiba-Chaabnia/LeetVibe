from __future__ import annotations

TOPIC: dict = {
    "title": "Simulation",
    "slug": "Simulation",
    "recognize": (
        "\"implement the rules exactly as described\", no optimisation needed,\n"
        "  \"game of life\", \"robot on a grid\", \"design a spreadsheet\",\n"
        "  step-by-step state machine, \"simulate the process\"."
    ),
    "diagram": (
        "  Recognition test: can you solve it by just doing what the problem says?\n"
        "  → YES: Simulation. No clever trick needed.\n"
        "\n"
        "  Common sub-patterns:\n"
        "  ┌──────────────────────────────────────────────────────────┐\n"
        "  │  In-place matrix mutation    → copy or use modular state │\n"
        "  │  Direction cycling           → dirs[(d+turn) % 4]        │\n"
        "  │  Spiral / layer traversal   → peel the matrix layer by layer│\n"
        "  │  State machine (few states) → match on current state     │\n"
        "  └──────────────────────────────────────────────────────────┘\n"
        "\n"
        "  The difficulty is usually implementation detail, not algorithm choice."
    ),
    "when": (
        "The problem describes a concrete process and asks you to execute it.\n"
        "  No pattern matching needed — read carefully, track state precisely."
    ),
    "pattern": (
        "# Spiral Matrix — peel layer by layer\n"
        "def spiral_order(matrix):\n"
        "    result = []\n"
        "    top, bottom, left, right = 0, len(matrix)-1, 0, len(matrix[0])-1\n"
        "    while top <= bottom and left <= right:\n"
        "        for c in range(left, right + 1):    result.append(matrix[top][c])\n"
        "        top += 1\n"
        "        for r in range(top, bottom + 1):    result.append(matrix[r][right])\n"
        "        right -= 1\n"
        "        if top <= bottom:\n"
        "            for c in range(right, left-1,-1): result.append(matrix[bottom][c])\n"
        "            bottom -= 1\n"
        "        if left <= right:\n"
        "            for r in range(bottom, top-1,-1): result.append(matrix[r][left])\n"
        "            left += 1\n"
        "    return result\n"
        "\n"
        "# Direction cycling — robot / snake movement\n"
        "DIRS = [(0,1),(1,0),(0,-1),(-1,0)]  # right, down, left, up\n"
        "d    = 0                              # current direction index\n"
        "r, c = 0, 0\n"
        "# turn right: d = (d + 1) % 4\n"
        "# turn left:  d = (d - 1) % 4  (Python: (d + 3) % 4 avoids negative)"
    ),
    "pattern2": (
        "# Game of Life — in-place with encoded states\n"
        "# Encode: 0=dead, 1=live, 2=was-live-now-dead, 3=was-dead-now-live\n"
        "def game_of_life(board):\n"
        "    rows, cols = len(board), len(board[0])\n"
        "    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]\n"
        "\n"
        "    def live_neighbours(r, c):\n"
        "        return sum(1 for dr,dc in DIRS\n"
        "                   if 0<=r+dr<rows and 0<=c+dc<cols\n"
        "                   and board[r+dr][c+dc] in (1, 2))  # 2 = was live\n"
        "\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            n = live_neighbours(r, c)\n"
        "            if board[r][c] == 1 and n not in (2, 3): board[r][c] = 2\n"
        "            elif board[r][c] == 0 and n == 3:        board[r][c] = 3\n"
        "    for r in range(rows):\n"
        "        for c in range(cols):\n"
        "            board[r][c] = 1 if board[r][c] in (1, 3) else 0\n"
        "\n"
        "# Rotate Matrix 90° clockwise in-place\n"
        "def rotate(matrix):\n"
        "    n = len(matrix)\n"
        "    for i in range(n):              # Step 1: transpose\n"
        "        for j in range(i+1, n):\n"
        "            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n"
        "    for row in matrix: row.reverse() # Step 2: reverse each row\n"
        "\n"
        "# Decode String — stack-based parser for k[encoded_string]\n"
        "# '3[a2[bc]]' → 'abcbcabcbcabcbc'\n"
        "def decode_string(s):\n"
        "    stack   = []   # stores (repeat_count, built_string_before_bracket)\n"
        "    current = ''\n"
        "    k       = 0\n"
        "    for ch in s:\n"
        "        if ch.isdigit():\n"
        "            k = k * 10 + int(ch)   # handle multi-digit numbers\n"
        "        elif ch == '[':\n"
        "            stack.append((k, current))  # save state\n"
        "            current, k = '', 0           # reset for inner block\n"
        "        elif ch == ']':\n"
        "            repeat, prev = stack.pop()\n"
        "            current = prev + current * repeat  # unwind\n"
        "        else:\n"
        "            current += ch\n"
        "    return current"
    ),
    "pitfalls": (
        "• In-place mutation during iteration: encode intermediate states\n"
        "  (like Game of Life 0-3) to avoid using the updated value as input.\n"
        "• Spiral Matrix: always check top<=bottom AND left<=right before the\n"
        "  third and fourth sweeps — a 1-row or 1-col matrix can double-count.\n"
        "• Direction cycling: (d - 1) % 4 is -1 % 4 = 3 in Python (correct),\n"
        "  but use (d + 3) % 4 to be explicit and language-agnostic.\n"
        "• Rotate matrix: transpose then reverse rows (not reverse then transpose)\n"
        "  for clockwise; transpose then reverse columns for counter-clockwise.\n"
        "• Decode String: handle multi-digit k (k = k*10 + int(ch)) before pushing\n"
        "  to stack — single-digit assumption breaks on inputs like '10[a]'."
    ),
    "time": "O(m × n)  for matrix problems  /  O(n) for sequence simulations",
    "space": "O(1)  in-place  /  O(m × n)  if output array needed",
    "problems": [
        ("Spiral Matrix",              "M"),
        ("Rotate Image",              "M"),
        ("Game of Life",              "M"),
        ("Robot Bounded in Circle",   "M"),
        ("Decode String",             "M"),
        ("Set Matrix Zeroes",         "M"),
        ("Design Tic-Tac-Toe",        "M"),
    ],
    "related": ["Arrays & Hashing", "Matrix / Grid", "Stack", "Queue"],
}
