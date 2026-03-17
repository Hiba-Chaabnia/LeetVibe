"""ReferenceGuideScreen — Concepts mode: algorithm topics with notes and export."""

from __future__ import annotations

import json
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from ..theme import AMBER, DIM, EMBER, FIRE, GOLD, GREEN, LAVA, RED
from ..widgets.status_bar import StatusBar
from .base import BaseScreen

# ── Notes persistence ──────────────────────────────────────────────────────────

_NOTES_DIR  = Path.home() / ".leetvibe"
_NOTES_FILE = _NOTES_DIR / "notes.json"


def _load_notes() -> dict[str, str]:
    try:
        return json.loads(_NOTES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_notes(notes: dict[str, str]) -> None:
    try:
        _NOTES_DIR.mkdir(parents=True, exist_ok=True)
        _NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ── Rich markup helper ─────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escape [ so Rich doesn't interpret user content as markup tags."""
    return text.replace("[", r"\[")


# ── Topic data ─────────────────────────────────────────────────────────────────

TOPICS: list[dict] = [
    {
        "title": "Arrays & Hashing",
        "slug": "Array",
        "diagram": (
            "  index:   0    1    2    3    4\n"
            "          ┌────┬────┬────┬────┬────┐\n"
            "  array:  │  2 │  7 │ 11 │ 15 │  3 │\n"
            "          └────┴────┴────┴────┴────┘\n"
            "\n"
            "  hash map { value → index }:\n"
            "  ┌──────────┬───────┐\n"
            "  │  key     │ value │\n"
            "  ├──────────┼───────┤\n"
            "  │  2       │   0   │\n"
            "  │  7       │   1   │\n"
            "  │  11      │   2   │\n"
            "  └──────────┴───────┘"
        ),
        "when": (
            "Fast O(1) lookups, counting frequencies, detecting duplicates,\n"
            "  or grouping elements by a computed key."
        ),
        "pattern": (
            "seen = {}\n"
            "for i, val in enumerate(arr):\n"
            "    complement = target - val\n"
            "    if complement in seen:\n"
            "        return [seen[complement], i]\n"
            "    seen[val] = i"
        ),
        "time": "O(n)",
        "space": "O(n)",
        "problems": [
            "Two Sum", "Contains Duplicate", "Group Anagrams",
            "Top K Frequent Elements", "Valid Anagram",
            "Product of Array Except Self",
        ],
    },
    {
        "title": "Two Pointers",
        "slug": "Two Pointers",
        "diagram": (
            "  sorted:  1    2    3    4    5    6\n"
            "           ↑                        ↑\n"
            "          left                    right\n"
            "\n"
            "  sum < target  →  left  += 1\n"
            "  sum > target  →  right -= 1\n"
            "  sum = target  →  found!"
        ),
        "when": (
            "Sorted array or linked list. Looking for a pair/triplet\n"
            "  satisfying a condition — replaces O(n²) nested loops."
        ),
        "pattern": (
            "left, right = 0, len(arr) - 1\n"
            "while left < right:\n"
            "    s = arr[left] + arr[right]\n"
            "    if   s == target:  return result\n"
            "    elif s <  target:  left  += 1\n"
            "    else:              right -= 1"
        ),
        "time": "O(n)",
        "space": "O(1)",
        "problems": [
            "Two Sum II", "3Sum", "Container With Most Water",
            "Trapping Rain Water", "Valid Palindrome",
        ],
    },
    {
        "title": "Sliding Window",
        "slug": "Sliding Window",
        "diagram": (
            "  a  b  c  d  e  f  g\n"
            "  ↑           ↑\n"
            " left        right        ← expand right each step\n"
            "\n"
            "  window violates condition:\n"
            "     ↑        ↑\n"
            "    left     right        ← shrink: left += 1\n"
            "\n"
            "  track: max/min/count of valid window"
        ),
        "when": (
            "Contiguous subarray or substring of variable/fixed size.\n"
            "  Finding longest or shortest window meeting a condition."
        ),
        "pattern": (
            "left = 0\n"
            "window = {}   # or running sum/count\n"
            "res = 0\n"
            "for right in range(len(s)):\n"
            "    window[s[right]] = window.get(s[right], 0) + 1\n"
            "    while invalid(window):        # shrink\n"
            "        window[s[left]] -= 1\n"
            "        left += 1\n"
            "    res = max(res, right - left + 1)"
        ),
        "time": "O(n)",
        "space": "O(k)   k = window size / alphabet",
        "problems": [
            "Longest Substring Without Repeating Characters",
            "Minimum Window Substring", "Permutation in String",
            "Longest Repeating Character Replacement",
            "Best Time to Buy and Sell Stock",
        ],
    },
    {
        "title": "Stack",
        "slug": "Stack",
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
            "  monotonic stack keeps sorted order:\n"
            "  increasing  →  next greater element\n"
            "  decreasing  →  next smaller element"
        ),
        "when": (
            "Matching brackets, undo/redo, next-greater-element,\n"
            "  expression evaluation, or iterative DFS."
        ),
        "pattern": (
            "stack = []\n"
            "for ch in s:\n"
            "    if ch in '({[':\n"
            "        stack.append(ch)\n"
            "    elif stack and matches(stack[-1], ch):\n"
            "        stack.pop()\n"
            "    else:\n"
            "        return False\n"
            "return not stack"
        ),
        "time": "O(n)",
        "space": "O(n)",
        "problems": [
            "Valid Parentheses", "Min Stack", "Daily Temperatures",
            "Largest Rectangle in Histogram",
            "Evaluate Reverse Polish Notation",
        ],
    },
    {
        "title": "Binary Search",
        "slug": "Binary Search",
        "diagram": (
            "  idx:  0    1    2    3    4    5    6\n"
            "  arr:  1    3    5    7    9   11   13\n"
            "                       ↑\n"
            "                      mid\n"
            "\n"
            "  target < arr[mid]  →  right = mid - 1\n"
            "  target > arr[mid]  →  left  = mid + 1\n"
            "  target = arr[mid]  →  found!\n"
            "\n"
            "  search space halves every iteration  →  O(log n)"
        ),
        "when": (
            "Sorted array, or any monotonic search space.\n"
            "  Finding a value, boundary, or minimum/maximum valid answer."
        ),
        "pattern": (
            "left, right = 0, len(arr) - 1\n"
            "while left <= right:\n"
            "    mid = (left + right) // 2\n"
            "    if   arr[mid] == target:  return mid\n"
            "    elif arr[mid] <  target:  left  = mid + 1\n"
            "    else:                     right = mid - 1\n"
            "return -1"
        ),
        "time": "O(log n)",
        "space": "O(1)",
        "problems": [
            "Binary Search", "Search in Rotated Sorted Array",
            "Find Minimum in Rotated Sorted Array",
            "Koko Eating Bananas", "Median of Two Sorted Arrays",
        ],
    },
    {
        "title": "Linked List",
        "slug": "Linked List",
        "diagram": (
            "  head\n"
            "   ↓\n"
            "  [1] → [2] → [3] → [4] → None\n"
            "\n"
            "  fast / slow pointers (Floyd's cycle):\n"
            "   s         f\n"
            "  [1] → [2] → [3] → [4] → [5]\n"
            "                ↑____________↑\n"
            "   slow steps +1, fast steps +2\n"
            "   meet inside cycle  →  cycle detected"
        ),
        "when": (
            "Reversals, cycle detection, finding the middle,\n"
            "  merging sorted lists, or removing the N-th node."
        ),
        "pattern": (
            "# Reverse a linked list\n"
            "prev, curr = None, head\n"
            "while curr:\n"
            "    nxt        = curr.next\n"
            "    curr.next  = prev\n"
            "    prev, curr = curr, nxt\n"
            "return prev\n"
            "\n"
            "# Fast / slow pointer (find middle)\n"
            "slow = fast = head\n"
            "while fast and fast.next:\n"
            "    slow, fast = slow.next, fast.next.next\n"
            "# slow is now at the middle"
        ),
        "time": "O(n)",
        "space": "O(1)",
        "problems": [
            "Reverse Linked List", "Merge Two Sorted Lists",
            "Linked List Cycle", "Remove Nth Node From End",
            "LRU Cache",
        ],
    },
    {
        "title": "Trees",
        "slug": "Tree",
        "diagram": (
            "           4\n"
            "          / \\\n"
            "         2   6\n"
            "        / \\ / \\\n"
            "       1  3 5  7\n"
            "\n"
            "  BFS level-order:  4  2  6  1  3  5  7\n"
            "  DFS inorder:      1  2  3  4  5  6  7\n"
            "  DFS preorder:     4  2  1  3  6  5  7\n"
            "  DFS postorder:    1  3  2  5  7  6  4"
        ),
        "when": (
            "Hierarchical data. Use DFS for path problems,\n"
            "  BFS for level-by-level or shortest-path in unweighted trees."
        ),
        "pattern": (
            "# DFS recursive\n"
            "def dfs(node):\n"
            "    if not node: return 0\n"
            "    left  = dfs(node.left)\n"
            "    right = dfs(node.right)\n"
            "    return 1 + max(left, right)\n"
            "\n"
            "# BFS iterative\n"
            "from collections import deque\n"
            "q = deque([root])\n"
            "while q:\n"
            "    node = q.popleft()\n"
            "    if node.left:  q.append(node.left)\n"
            "    if node.right: q.append(node.right)"
        ),
        "time": "O(n)",
        "space": "O(h)   h = height  (O(n) worst case)",
        "problems": [
            "Invert Binary Tree", "Maximum Depth of Binary Tree",
            "Lowest Common Ancestor of a BST",
            "Binary Tree Level Order Traversal",
            "Validate Binary Search Tree",
        ],
    },
    {
        "title": "Tries",
        "slug": "Trie",
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
            "      *  *  *    (* = end of word)\n"
            "\n"
            '  search("cat") → root→c→a→t  → found'
        ),
        "when": (
            "Prefix search, autocomplete, spell-checking,\n"
            "  or grouping words by shared prefixes."
        ),
        "pattern": (
            "class TrieNode:\n"
            "    def __init__(self):\n"
            "        self.children = {}\n"
            "        self.is_end   = False\n"
            "\n"
            "class Trie:\n"
            "    def __init__(self):\n"
            "        self.root = TrieNode()\n"
            "    def insert(self, word):\n"
            "        node = self.root\n"
            "        for ch in word:\n"
            "            node = node.children.setdefault(ch, TrieNode())\n"
            "        node.is_end = True"
        ),
        "time": "O(m)   m = word length",
        "space": "O(m × n)   n = number of words",
        "problems": [
            "Implement Trie", "Word Search II",
            "Design Add and Search Words Data Structure",
            "Replace Words", "Longest Common Prefix",
        ],
    },
    {
        "title": "Heap / Priority Queue",
        "slug": "Heap (Priority Queue)",
        "diagram": (
            "  min-heap:       1              max-heap:      9\n"
            "                / \\                            / \\\n"
            "               3   2                          7   8\n"
            "              / \\ / \\                        / \\ / \\\n"
            "             7  4 5  6                      4  6 5  3\n"
            "\n"
            "  push   O(log n)    pop    O(log n)    peek  O(1)\n"
            "  heapify entire list  →  O(n)  (not n log n)"
        ),
        "when": (
            "Top-K elements, streaming medians, task scheduling,\n"
            "  Dijkstra's shortest path, or merging K sorted lists."
        ),
        "pattern": (
            "import heapq\n"
            "\n"
            "# Min-heap (Python default)\n"
            "heap = []\n"
            "heapq.heappush(heap, val)\n"
            "smallest = heapq.heappop(heap)\n"
            "\n"
            "# Max-heap: negate values\n"
            "heapq.heappush(heap, -val)\n"
            "largest = -heapq.heappop(heap)\n"
            "\n"
            "# Top K largest in O(n log k)\n"
            "return heapq.nlargest(k, nums)"
        ),
        "time": "O(n log n)  for sorted stream  /  O(n log k) top-K",
        "space": "O(k)   for top-K heap",
        "problems": [
            "Kth Largest Element in an Array",
            "Top K Frequent Elements",
            "Find Median from Data Stream",
            "Merge K Sorted Lists", "Task Scheduler",
        ],
    },
    {
        "title": "Backtracking",
        "slug": "Backtracking",
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
            "  pattern:  choose → explore → unchoose"
        ),
        "when": (
            "Generating all combinations, permutations, or subsets.\n"
            "  Constraint-satisfaction (N-Queens, Sudoku, Word Search)."
        ),
        "pattern": (
            "def backtrack(start, path):\n"
            "    result.append(path[:])       # record state\n"
            "    for i in range(start, len(nums)):\n"
            "        path.append(nums[i])     # choose\n"
            "        backtrack(i + 1, path)   # explore\n"
            "        path.pop()               # unchoose\n"
            "\n"
            "result = []\n"
            "backtrack(0, [])\n"
            "return result"
        ),
        "time": "O(2ⁿ) subsets   /   O(n!) permutations",
        "space": "O(n)   recursion depth",
        "problems": [
            "Subsets", "Combination Sum", "Permutations",
            "N-Queens", "Word Search", "Palindrome Partitioning",
        ],
    },
    {
        "title": "Graphs",
        "slug": "Graph",
        "diagram": (
            "  adjacency list:\n"
            "  0: [1, 2]          0 ── 1 ── 3\n"
            "  1: [0, 3]          │\n"
            "  2: [0, 4]          2 ── 4\n"
            "  3: [1]\n"
            "  4: [2]\n"
            "\n"
            "  BFS → queue    shortest path, unweighted\n"
            "  DFS → stack    connectivity, cycles, topo sort"
        ),
        "when": (
            "Network traversal, connectivity, shortest path, cycle detection,\n"
            "  topological sort, or island/region counting."
        ),
        "pattern": (
            "from collections import deque\n"
            "\n"
            "# BFS — shortest path\n"
            "visited = {start}\n"
            "q = deque([(start, 0)])\n"
            "while q:\n"
            "    node, dist = q.popleft()\n"
            "    if node == target: return dist\n"
            "    for nei in graph[node]:\n"
            "        if nei not in visited:\n"
            "            visited.add(nei)\n"
            "            q.append((nei, dist + 1))"
        ),
        "time": "O(V + E)",
        "space": "O(V)",
        "problems": [
            "Number of Islands", "Clone Graph",
            "Course Schedule", "Pacific Atlantic Water Flow",
            "Word Ladder", "Rotting Oranges",
        ],
    },
    {
        "title": "Dynamic Programming",
        "slug": "Dynamic Programming",
        "diagram": (
            "  Fibonacci (1D DP):\n"
            "  dp[n] = dp[n-1] + dp[n-2]\n"
            "  [ 0, 1, 1, 2, 3, 5, 8, 13, ... ]\n"
            "\n"
            '  LCS (2D DP)  s1="ace"  s2="abcde":\n'
            '      \"\"  a  b  c  d  e\n'
            '   \"\" [ 0  0  0  0  0  0 ]\n'
            '    a [ 0  1  1  1  1  1 ]\n'
            '    c [ 0  1  1  2  2  2 ]\n'
            '    e [ 0  1  1  2  2  3 ]  ← answer = 3'
        ),
        "when": (
            "Overlapping subproblems + optimal substructure.\n"
            "  Counting ways, min/max cost, longest subsequences."
        ),
        "pattern": (
            "# Top-down (memoization)\n"
            "from functools import cache\n"
            "@cache\n"
            "def dp(i):\n"
            "    if i <= 1: return i\n"
            "    return dp(i - 1) + dp(i - 2)\n"
            "\n"
            "# Bottom-up (tabulation)\n"
            "dp = [0] * (n + 1)\n"
            "dp[1] = 1\n"
            "for i in range(2, n + 1):\n"
            "    dp[i] = dp[i - 1] + dp[i - 2]"
        ),
        "time": "O(n) 1D   /   O(m × n) 2D",
        "space": "O(n)  or  O(1) with rolling-array optimisation",
        "problems": [
            "Climbing Stairs", "House Robber", "Coin Change",
            "Longest Increasing Subsequence",
            "Longest Common Subsequence", "0/1 Knapsack",
        ],
    },
    {
        "title": "Greedy",
        "slug": "Greedy",
        "diagram": (
            "  Activity selection — earliest finish first:\n"
            "\n"
            "  A: ─────────\n"
            "  B:      ─────────    ← A chosen (ends first)\n"
            "  C:           ─────   ← C chosen (next after A)\n"
            "  D:                ── ← D chosen\n"
            "       0   3   5   7   9\n"
            "\n"
            "  local optimum  →  global optimum"
        ),
        "when": (
            "Local optimum reliably leads to global optimum.\n"
            "  Interval scheduling, jump games, fractional knapsack."
        ),
        "pattern": (
            "# Jump Game II — minimum jumps\n"
            "jumps = farthest = end = 0\n"
            "for i in range(len(nums) - 1):\n"
            "    farthest = max(farthest, i + nums[i])\n"
            "    if i == end:            # must jump\n"
            "        jumps += 1\n"
            "        end = farthest\n"
            "return jumps"
        ),
        "time": "O(n log n) with sorting   /   O(n) otherwise",
        "space": "O(1)",
        "problems": [
            "Jump Game", "Jump Game II", "Gas Station",
            "Hand of Straights", "Merge Intervals", "Partition Labels",
        ],
    },
    {
        "title": "Intervals",
        "slug": "Intervals",
        "diagram": (
            "  merge overlapping intervals:\n"
            "\n"
            "  input:   [1──3]  [2────5]  [6──8]  [9─10]\n"
            "\n"
            "  sort by start, then merge if overlap:\n"
            "  output:  [1────────5]      [6──8]  [9─10]\n"
            "\n"
            "  overlap condition:  next.start  <=  current.end"
        ),
        "when": (
            "Scheduling, calendar conflicts, merging ranges,\n"
            "  or finding gaps / minimum coverage."
        ),
        "pattern": (
            "# Merge intervals\n"
            "intervals.sort(key=lambda x: x[0])\n"
            "merged = [intervals[0]]\n"
            "for start, end in intervals[1:]:\n"
            "    if start <= merged[-1][1]:\n"
            "        merged[-1][1] = max(merged[-1][1], end)\n"
            "    else:\n"
            "        merged.append([start, end])\n"
            "return merged"
        ),
        "time": "O(n log n)",
        "space": "O(n)",
        "problems": [
            "Merge Intervals", "Insert Interval",
            "Non-overlapping Intervals", "Meeting Rooms",
            "Meeting Rooms II",
            "Minimum Interval to Include Each Query",
        ],
    },
    {
        "title": "Bit Manipulation",
        "slug": "Bit Manipulation",
        "diagram": (
            "  AND  &    OR  |    XOR  ^    NOT  ~\n"
            "   1&1=1   1|0=1   1^1=0   ~1= 0\n"
            "   1&0=0   0|0=0   1^0=1   ~0= 1\n"
            "\n"
            "  n & (n-1)   →  clears lowest set bit\n"
            "  n & (-n)    →  isolates lowest set bit\n"
            "  n >> 1      →  floor divide by 2\n"
            "  n << 1      →  multiply by 2\n"
            "  a ^ b ^ b   →  a   (XOR cancels pairs)"
        ),
        "when": (
            "Binary representations, bitmask flags, counting set bits,\n"
            "  or finding unique elements among duplicates."
        ),
        "pattern": (
            "# Count set bits — Brian Kernighan\n"
            "count = 0\n"
            "while n:\n"
            "    n &= n - 1       # clear lowest set bit\n"
            "    count += 1\n"
            "\n"
            "# Find single number (XOR cancels duplicates)\n"
            "result = 0\n"
            "for num in nums:\n"
            "    result ^= num\n"
            "return result"
        ),
        "time": "O(1) bitwise ops   /   O(log n) for n bits",
        "space": "O(1)",
        "problems": [
            "Single Number", "Number of 1 Bits",
            "Counting Bits", "Reverse Bits",
            "Missing Number", "Sum of Two Integers",
        ],
    },
]


# ── Content renderer ───────────────────────────────────────────────────────────

def _render_topic(topic: dict, note: str) -> str:
    """Build a Rich-markup string for the right panel."""
    title   = topic["title"]
    diagram = _esc(topic["diagram"])
    when    = _esc(topic["when"])
    pattern = _esc(topic["pattern"])
    t_val   = _esc(topic["time"])
    s_val   = _esc(topic["space"])

    lines: list[str] = [
        f"[bold {FIRE}]━━━  {title}  ━━━[/bold {FIRE}]",
        "",
        f"[{GOLD}]Diagram[/{GOLD}]",
        f"[dim]{'─' * 44}[/dim]",
    ]
    lines += [f"  {ln}" for ln in diagram.split("\n")]
    lines += [
        f"[dim]{'─' * 44}[/dim]",
        "",
        f"[{GOLD}]When to use[/{GOLD}]",
    ]
    lines += [f"  {ln}" for ln in when.split("\n")]
    lines += [
        "",
        f"[{GOLD}]Pattern[/{GOLD}]",
        f"[dim]─── python {'─' * 33}[/dim]",
    ]
    lines += [f"  {ln}" for ln in pattern.split("\n")]
    lines += [
        f"[dim]{'─' * 44}[/dim]",
        "",
        f"[{GOLD}]Complexity[/{GOLD}]",
        f"  Time    [{AMBER}]{t_val}[/{AMBER}]",
        f"  Space   [{AMBER}]{s_val}[/{AMBER}]",
        "",
        f"[{GOLD}]Classic Problems[/{GOLD}]",
    ]
    for prob in topic["problems"]:
        lines.append(f"  [{DIM}]•[/{DIM}] {_esc(prob)}")
    lines.append("")

    # Notes section
    if note.strip():
        lines.append(f"[{GOLD}]My Notes[/{GOLD}]")
        for note_line in note.strip().split("\n"):
            lines.append(f"  {_esc(note_line)}")
    else:
        lines.append(f"[{DIM}]No notes yet — press [bold]N[/bold] to add one.[/{DIM}]")

    return "\n".join(lines)


# ── Screen ─────────────────────────────────────────────────────────────────────

class ReferenceGuideScreen(BaseScreen):
    """Concepts mode — browse algorithm topics, add notes, and export to DOCX."""

    BINDINGS = [
        Binding("escape",  "pop_screen",   "← Back"),
        Binding("ctrl+q",  "quit_app",     "Quit"),
        Binding("e",       "explain_more", "Explain More",  show=False),
        Binding("p",       "practice",     "Practice",      show=False),
        Binding("n",       "edit_note",    "Edit Note",     show=False),
        Binding("x",       "export_docx",  "Export DOCX",   show=False),
    ]

    DEFAULT_CSS = f"""
    ReferenceGuideScreen {{
        background: #121212;
    }}
    #ref-body {{
        height: 1fr;
    }}
    #ref-topics {{
        width: 26;
        border-right: solid {FIRE};
        background: #0e0e0e;
        padding: 0;
    }}
    #ref-topics OptionList {{
        height: 1fr;
        background: transparent;
        border: none;
        padding: 1 0;
        scrollbar-size: 1 1;
    }}
    #ref-content-scroll {{
        width: 1fr;
        padding: 1 2;
        scrollbar-size: 1 1;
    }}
    #ref-content {{
        width: 100%;
        height: auto;
    }}
    #ref-status {{
        background: #121212;
    }}
    """

    def __init__(self) -> None:
        super().__init__()
        self._current_idx: int = 0
        self._notes: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        with Horizontal(id="ref-body"):
            with VerticalScroll(id="ref-topics"):
                yield OptionList(
                    *[Option(t["title"], id=f"topic-{i}") for i, t in enumerate(TOPICS)],
                    id="topic-list",
                )
            with VerticalScroll(id="ref-content-scroll"):
                yield Static("", id="ref-content", markup=True)

        yield StatusBar(
            hints=[
                ("↑↓",     "navigate topics",  None),
                ("E",      "explain more",     self.action_explain_more),
                ("P",      "practice",         self.action_practice),
                ("N",      "edit note",        self.action_edit_note),
                ("X",      "export DOCX",      self.action_export_docx),
                ("Esc",    "go back",          self.action_pop_screen),
                ("Ctrl+Q", "quit",             self.action_quit_app),
            ],
            id="ref-status",
        )

    def on_mount(self) -> None:
        self._notes = _load_notes()
        topic_list = self.query_one("#topic-list", OptionList)
        topic_list.focus()
        topic_list.highlighted = 0
        self._refresh_content()

    # ── Topic navigation ────────────────────────────────────────────────

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self._current_idx = event.option_index
        self._refresh_content()

    def _refresh_content(self) -> None:
        topic = TOPICS[self._current_idx]
        note  = self._notes.get(topic["slug"], "")
        try:
            self.query_one("#ref-content", Static).update(_render_topic(topic, note))
            # Scroll content back to top when topic changes
            scroll = self.query_one("#ref-content-scroll", VerticalScroll)
            scroll.scroll_home(animate=False)
        except Exception:
            pass

    # ── Actions ─────────────────────────────────────────────────────────

    def action_explain_more(self) -> None:
        """Open an AI session explaining the current topic in depth."""
        from ...challenge_loader import Challenge
        from .agent_session import AgentSessionScreen

        topic = TOPICS[self._current_idx]
        synthetic = Challenge(
            id=f"concept-{topic['slug'].lower().replace(' ', '-').replace('(', '').replace(')', '')}",
            title=f"Concept: {topic['title']}",
            difficulty="easy",
            description=(
                f"Explain the **{topic['title']}** algorithm pattern in depth.\n\n"
                f"Please cover:\n"
                f"1. The core idea and intuition behind this pattern\n"
                f"2. A step-by-step walkthrough with a concrete example\n"
                f"3. Common pitfalls and edge cases to watch for\n"
                f"4. How to recognise this pattern when reading a problem\n"
                f"5. Time and space complexity analysis\n\n"
                f"Use the following classic problems as examples where appropriate:\n"
                + "\n".join(f"- {p}" for p in topic["problems"])
            ),
            topics=[topic["slug"]],
        )
        self.app.push_screen(AgentSessionScreen(synthetic, mode="learn"))

    def action_practice(self) -> None:
        """Open challenge list pre-filtered to the current topic."""
        from .challenge_list import ChallengeListScreen
        topic = TOPICS[self._current_idx]
        self.app.push_screen(ChallengeListScreen(mode="learn", initial_topic=topic["slug"]))

    def action_edit_note(self) -> None:
        """Open the notes modal for the current topic."""
        from .notes_modal import NotesModal
        topic    = TOPICS[self._current_idx]
        existing = self._notes.get(topic["slug"], "")

        def _on_result(result: str | None) -> None:
            if result is not None:
                self._notes[topic["slug"]] = result
                _save_notes(self._notes)
                self._refresh_content()
                self.notify(
                    f"Note saved for {topic['title']}",
                    severity="information",
                )

        self.app.push_screen(NotesModal(topic["title"], existing), _on_result)

    def action_export_docx(self) -> None:
        """Export all topics and notes to a DOCX file in a background thread."""
        self.notify("Exporting…", severity="information")
        self._run_export()

    @work(thread=True)
    def _run_export(self) -> None:
        try:
            from ...docx_exporter import export_reference_docx
            path = export_reference_docx(TOPICS, self._notes)
            self.app.call_from_thread(
                self.notify,
                f"Saved → {path}",
                severity="information",
                timeout=8,
            )
        except ImportError:
            self.app.call_from_thread(
                self.notify,
                "python-docx not installed — run: pip install python-docx",
                severity="error",
            )
        except Exception as exc:
            self.app.call_from_thread(
                self.notify,
                f"Export failed: {str(exc).replace('[', '(').replace(']', ')')}",
                severity="error",
            )
