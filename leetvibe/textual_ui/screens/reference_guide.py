"""ReferenceGuideScreen — Playbook mode: algorithm topics with notes and export."""

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


# ── Difficulty badge helpers ───────────────────────────────────────────────────

_DIFF_COLOR = {"E": GREEN, "M": AMBER, "H": RED}
_DIFF_LABEL = {"E": "Easy", "M": "Med ", "H": "Hard"}


# ── Topic data ─────────────────────────────────────────────────────────────────
# problems: list of (name, difficulty) tuples — difficulty "E" | "M" | "H"
# pattern2: optional second code variant
# recognize: keyword/constraint signals that indicate this pattern
# pitfalls:  common mistakes and gotchas
# related:   list of related topic titles

TOPICS: list[dict] = [
    # ── 0. Pattern Selector ───────────────────────────────────────────────
    {
        "title": "▶  Pattern Selector",
        "slug": "_selector",
        "recognize": "",
        "diagram": (
            "  Read the problem statement. Match keywords to a pattern:\n"
            "\n"
            "  KEYWORD / CONSTRAINT                   PATTERN\n"
            "  ──────────────────────────────────────────────────────\n"
            "  \"contiguous subarray\"                → Sliding Window\n"
            "  sorted array + pair / triplet         → Two Pointers\n"
            "  sorted + find value / O(log n)        → Binary Search\n"
            "  \"minimum / maximum valid answer\"      → Binary Search on Answer\n"
            "  range sum / subarray sum = k          → Prefix Sum\n"
            "  all combinations / permutations       → Backtracking\n"
            "  shortest path, unweighted graph       → BFS (Graphs)\n"
            "  shortest path, weighted (≥ 0)         → Dijkstra\n"
            "  \"connected\" / \"same group\" / merge    → Union Find\n"
            "  prerequisites / dependency order      → Topological Sort\n"
            "  next greater / next smaller element   → Monotonic Stack\n"
            "  top-K / streaming median              → Heap\n"
            "  prefix / autocomplete / word search   → Trie\n"
            "  overlapping subproblems + count/min   → Dynamic Programming\n"
            "  local choice → global optimum         → Greedy\n"
            "  scheduling / overlapping ranges       → Intervals\n"
            "  grid / matrix / island / flood fill   → Matrix / Grid\n"
            "  unique among pairs / XOR trick        → Bit Manipulation\n"
            "  prime / GCD / power / modular math    → Math Patterns\n"
        ),
        "when": (
            "Start here when you don't immediately recognise the pattern.\n"
            "  Scan for keywords, then jump to the matching topic."
        ),
        "pattern": "",
        "pattern2": "",
        "pitfalls": "",
        "time": "",
        "space": "",
        "problems": [],
        "related": [],
    },

    # ── 1. Arrays & Hashing ───────────────────────────────────────────────
    {
        "title": "Arrays & Hashing",
        "slug": "Array",
        "recognize": (
            "\"duplicate\", \"count frequency\", \"group by\", \"two elements\"\n"
            "  satisfying a sum condition, anagram detection."
        ),
        "diagram": (
            "  index:   0    1    2    3    4\n"
            "          ┌────┬────┬────┬────┬────┐\n"
            "  array:  │  2 │  7 │ 11 │ 15 │  3 │\n"
            "          └────┴────┴────┴────┴────┘\n"
            "\n"
            "  hash map { value → index }:\n"
            "  ┌────────┬───────┐\n"
            "  │  key   │ value │\n"
            "  ├────────┼───────┤\n"
            "  │  2     │   0   │\n"
            "  │  7     │   1   │\n"
            "  │  11    │   2   │\n"
            "  └────────┴───────┘"
        ),
        "when": (
            "Fast O(1) lookups, counting frequencies, detecting duplicates,\n"
            "  or grouping elements by a computed key."
        ),
        "pattern": (
            "# Two Sum — look up complement in hash map\n"
            "seen = {}\n"
            "for i, val in enumerate(arr):\n"
            "    complement = target - val\n"
            "    if complement in seen:\n"
            "        return [seen[complement], i]\n"
            "    seen[val] = i"
        ),
        "pattern2": (
            "# Group Anagrams — hash by sorted key\n"
            "from collections import defaultdict\n"
            "groups = defaultdict(list)\n"
            "for word in words:\n"
            "    key = tuple(sorted(word))   # or tuple(Counter(word).items())\n"
            "    groups[key].append(word)\n"
            "return list(groups.values())"
        ),
        "pitfalls": (
            "• defaultdict vs plain dict — plain dict raises KeyError on missing key.\n"
            "• Counter is not a set; it counts duplicates, not deduplicates.\n"
            "• tuple(sorted()) works as a dict key; list is unhashable."
        ),
        "time": "O(n)",
        "space": "O(n)",
        "problems": [
            ("Two Sum",                      "E"),
            ("Contains Duplicate",           "E"),
            ("Valid Anagram",                "E"),
            ("Group Anagrams",               "M"),
            ("Top K Frequent Elements",      "M"),
            ("Product of Array Except Self", "M"),
            ("Longest Consecutive Sequence", "M"),
        ],
        "related": ["Sliding Window", "Two Pointers"],
    },

    # ── 2. Prefix Sum ─────────────────────────────────────────────────────
    {
        "title": "Prefix Sum",
        "slug": "Prefix Sum",
        "recognize": (
            "\"subarray sum equals k\", \"range sum query\",\n"
            "  \"find pivot index\", multiple range queries on the same array."
        ),
        "diagram": (
            "  arr:    [ 3,  1,  4,  1,  5 ]\n"
            "  prefix: [ 0,  3,  4,  8,  9, 14 ]   (prefix[0] = 0 sentinel)\n"
            "\n"
            "  sum(arr[l..r])  =  prefix[r+1] - prefix[l]\n"
            "\n"
            "  e.g. sum(arr[1..3]) = prefix[4] - prefix[1]\n"
            "                      =    9       -    3    = 6"
        ),
        "when": (
            "Multiple range-sum queries on a static array.\n"
            "  Counting subarrays whose sum equals a target."
        ),
        "pattern": (
            "# Build prefix sum — O(n) build, O(1) per query\n"
            "prefix = [0] * (len(arr) + 1)\n"
            "for i, v in enumerate(arr):\n"
            "    prefix[i + 1] = prefix[i] + v\n"
            "\n"
            "def range_sum(l, r):           # inclusive [l, r]\n"
            "    return prefix[r + 1] - prefix[l]"
        ),
        "pattern2": (
            "# Subarray sum equals k — hash map of running prefix sums\n"
            "from collections import defaultdict\n"
            "count = defaultdict(int, {0: 1})   # seed: empty prefix\n"
            "running, res = 0, 0\n"
            "for v in nums:\n"
            "    running += v\n"
            "    res    += count[running - k]    # seen this prefix before?\n"
            "    count[running] += 1\n"
            "return res"
        ),
        "pitfalls": (
            "• Off-by-one: use prefix[0]=0 sentinel; query is prefix[r+1]-prefix[l].\n"
            "• Subarray sum = k: seed count[0]=1 BEFORE the loop.\n"
            "• Difference array for range updates: add delta at l, subtract at r+1."
        ),
        "time": "O(n) build  /  O(1) per query",
        "space": "O(n)",
        "problems": [
            ("Range Sum Query - Immutable",      "E"),
            ("Find Pivot Index",                 "E"),
            ("Subarray Sum Equals K",            "M"),
            ("Product of Array Except Self",     "M"),
            ("Contiguous Array",                 "M"),
            ("Count of Range Sum",               "H"),
        ],
        "related": ["Arrays & Hashing", "Sliding Window"],
    },

    # ── 3. Two Pointers ───────────────────────────────────────────────────
    {
        "title": "Two Pointers",
        "slug": "Two Pointers",
        "recognize": (
            "sorted array + find pair/triplet, palindrome check,\n"
            "  merge two sorted arrays, remove duplicates in-place."
        ),
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
            "# Two Sum II — sorted array\n"
            "left, right = 0, len(arr) - 1\n"
            "while left < right:\n"
            "    s = arr[left] + arr[right]\n"
            "    if   s == target:  return [left + 1, right + 1]\n"
            "    elif s <  target:  left  += 1\n"
            "    else:              right -= 1"
        ),
        "pattern2": (
            "# 3Sum — fix one element, two-pointer on the rest\n"
            "nums.sort()\n"
            "res = []\n"
            "for i in range(len(nums) - 2):\n"
            "    if i > 0 and nums[i] == nums[i - 1]: continue  # skip dupe\n"
            "    l, r = i + 1, len(nums) - 1\n"
            "    while l < r:\n"
            "        s = nums[i] + nums[l] + nums[r]\n"
            "        if   s == 0: res.append([nums[i], nums[l], nums[r]]); l += 1; r -= 1\n"
            "        elif s <  0: l += 1\n"
            "        else:        r -= 1\n"
            "        while l < r and nums[l] == nums[l - 1]: l += 1  # skip dupe\n"
            "        while l < r and nums[r] == nums[r + 1]: r -= 1  # skip dupe"
        ),
        "pitfalls": (
            "• 3Sum: skip duplicate values at i, l, r to avoid duplicate triplets.\n"
            "• Array must be sorted first — don't forget nums.sort().\n"
            "• Loop condition is left < right (strict), not <=."
        ),
        "time": "O(n) pair  /  O(n²) triplet",
        "space": "O(1)  (excluding output)",
        "problems": [
            ("Valid Palindrome",           "E"),
            ("Two Sum II",                 "M"),
            ("3Sum",                       "M"),
            ("Container With Most Water",  "M"),
            ("Trapping Rain Water",        "H"),
        ],
        "related": ["Sliding Window", "Binary Search"],
    },

    # ── 4. Sliding Window ─────────────────────────────────────────────────
    {
        "title": "Sliding Window",
        "slug": "Sliding Window",
        "recognize": (
            "\"contiguous subarray\", \"substring\", \"window\",\n"
            "  longest/shortest meeting a condition, fixed-size subarray stat."
        ),
        "diagram": (
            "  Variable window (expand right, shrink left when invalid):\n"
            "  a  b  c  d  e  f  g\n"
            "  ↑           ↑\n"
            " left        right        ← expand right each step\n"
            "\n"
            "  window violates condition:\n"
            "     ↑        ↑\n"
            "    left     right        ← shrink: left += 1"
        ),
        "when": (
            "Contiguous subarray or substring of variable or fixed size.\n"
            "  Finding longest or shortest window meeting a condition."
        ),
        "pattern": (
            "# Variable window — longest substring with at most k distinct chars\n"
            "left = 0\n"
            "window = {}\n"
            "res = 0\n"
            "for right in range(len(s)):\n"
            "    window[s[right]] = window.get(s[right], 0) + 1\n"
            "    while len(window) > k:          # shrink until valid\n"
            "        window[s[left]] -= 1\n"
            "        if window[s[left]] == 0: del window[s[left]]\n"
            "        left += 1\n"
            "    res = max(res, right - left + 1)\n"
            "return res"
        ),
        "pattern2": (
            "# Fixed window — maximum sum of size k\n"
            "window_sum = sum(nums[:k])\n"
            "best = window_sum\n"
            "for i in range(k, len(nums)):\n"
            "    window_sum += nums[i] - nums[i - k]\n"
            "    best = max(best, window_sum)\n"
            "return best"
        ),
        "pitfalls": (
            "• Window size formula: right - left + 1 (both ends inclusive).\n"
            "• Fixed window: slide by adding nums[i] and subtracting nums[i-k].\n"
            "• Variable inner while is O(n) amortised — each element enters/leaves once."
        ),
        "time": "O(n)  — each element enters and leaves the window at most once",
        "space": "O(k)  k = window constraint / alphabet size",
        "problems": [
            ("Best Time to Buy and Sell Stock",            "E"),
            ("Longest Substring Without Repeating Chars",  "M"),
            ("Permutation in String",                      "M"),
            ("Longest Repeating Character Replacement",    "M"),
            ("Minimum Window Substring",                   "H"),
            ("Sliding Window Maximum",                     "H"),
        ],
        "related": ["Two Pointers", "Prefix Sum"],
    },

    # ── 5. Stack ──────────────────────────────────────────────────────────
    {
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
        "related": ["Monotonic Stack", "Graphs"],
    },

    # ── 6. Monotonic Stack ────────────────────────────────────────────────
    {
        "title": "Monotonic Stack",
        "slug": "Monotonic Stack",
        "recognize": (
            "\"next greater element\", \"next smaller\", \"previous larger\",\n"
            "  \"daily temperatures\", histogram areas, stock span."
        ),
        "diagram": (
            "  Find next greater element — decreasing stack:\n"
            "  arr:  [ 2,  1,  5,  3,  6,  4 ]\n"
            "\n"
            "  i=0: push 0          stack: [0]     (indices)\n"
            "  i=1: push 1          stack: [0,1]\n"
            "  i=2: 5>arr[1] pop→res[1]=5; 5>arr[0] pop→res[0]=5; push 2\n"
            "  i=3: push 3          stack: [2,3]\n"
            "  i=4: 6>arr[3] pop→res[3]=6; 6>arr[2] pop→res[2]=6; push 4\n"
            "  i=5: push 5          stack: [4,5]\n"
            "  remaining → -1:  res[4]=-1, res[5]=-1"
        ),
        "when": (
            "Problems requiring the next or previous element that is strictly\n"
            "  larger or smaller. Histogram-area problems use a variation."
        ),
        "pattern": (
            "# Next Greater Element — store indices in stack\n"
            "res = [-1] * len(arr)\n"
            "stack = []         # indices, not values\n"
            "for i in range(len(arr)):\n"
            "    while stack and arr[i] > arr[stack[-1]]:\n"
            "        idx = stack.pop()\n"
            "        res[idx] = arr[i]  # arr[i] is the next greater\n"
            "    stack.append(i)\n"
            "return res"
        ),
        "pattern2": (
            "# Largest Rectangle in Histogram\n"
            "stack = []   # (start_index, height)\n"
            "max_area = 0\n"
            "for i, h in enumerate(heights):\n"
            "    start = i\n"
            "    while stack and stack[-1][1] > h:\n"
            "        idx, ht = stack.pop()\n"
            "        max_area = max(max_area, ht * (i - idx))\n"
            "        start = idx\n"
            "    stack.append((start, h))\n"
            "for idx, ht in stack:\n"
            "    max_area = max(max_area, ht * (len(heights) - idx))\n"
            "return max_area"
        ),
        "pitfalls": (
            "• Decreasing stack → next greater; increasing stack → next smaller.\n"
            "• Store indices (not values) so you can compute span/width.\n"
            "• After the loop, elements left on the stack have no next greater — set -1."
        ),
        "time": "O(n)  — each element pushed and popped at most once",
        "space": "O(n)",
        "problems": [
            ("Daily Temperatures",              "M"),
            ("Next Greater Element I",          "E"),
            ("Car Fleet",                       "M"),
            ("Largest Rectangle in Histogram",  "H"),
            ("Trapping Rain Water",             "H"),
        ],
        "related": ["Stack", "Sliding Window"],
    },

    # ── 7. Binary Search ──────────────────────────────────────────────────
    {
        "title": "Binary Search",
        "slug": "Binary Search",
        "recognize": (
            "sorted array, \"O(log n) required\", \"minimum / maximum valid answer\",\n"
            "  any monotonic feasibility condition on an answer space."
        ),
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
            "  Finding a value, a boundary, or the min/max valid answer."
        ),
        "pattern": (
            "# Find exact value\n"
            "left, right = 0, len(arr) - 1\n"
            "while left <= right:\n"
            "    mid = left + (right - left) // 2   # avoids overflow\n"
            "    if   arr[mid] == target:  return mid\n"
            "    elif arr[mid] <  target:  left  = mid + 1\n"
            "    else:                     right = mid - 1\n"
            "return -1"
        ),
        "pattern2": (
            "# Binary search on the answer space\n"
            "# e.g. minimum speed such that feasible(speed) is True\n"
            "left, right = lo, hi          # define the answer range\n"
            "while left < right:           # converges to smallest valid\n"
            "    mid = (left + right) // 2\n"
            "    if feasible(mid):         # monotonic: once True, stays True\n"
            "        right = mid           # mid could be the answer\n"
            "    else:\n"
            "        left = mid + 1\n"
            "return left"
        ),
        "pitfalls": (
            "• Exact search: left <= right. Boundary search: left < right.\n"
            "• mid = left + (right - left) // 2 prevents integer overflow.\n"
            "• Boundary: when feasible(mid) is True set right=mid (NOT mid-1)."
        ),
        "time": "O(log n)",
        "space": "O(1)",
        "problems": [
            ("Binary Search",                        "E"),
            ("Search in Rotated Sorted Array",        "M"),
            ("Find Minimum in Rotated Sorted Array",  "M"),
            ("Koko Eating Bananas",                   "M"),
            ("Time Based Key-Value Store",            "M"),
            ("Median of Two Sorted Arrays",           "H"),
        ],
        "related": ["Two Pointers", "Heap / Priority Queue"],
    },

    # ── 8. Linked List ────────────────────────────────────────────────────
    {
        "title": "Linked List",
        "slug": "Linked List",
        "recognize": (
            "reversal, cycle detection, find middle, merge sorted lists,\n"
            "  remove N-th from end, reorder list."
        ),
        "diagram": (
            "  head\n"
            "   ↓\n"
            "  [1] → [2] → [3] → [4] → None\n"
            "\n"
            "  fast / slow pointers (Floyd's cycle detection):\n"
            "   s         f\n"
            "  [1] → [2] → [3] → [4] → [5]\n"
            "                ↑____________↑\n"
            "   slow +1, fast +2 → meet inside cycle → cycle exists"
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
            "# Find middle (slow/fast)\n"
            "slow = fast = head\n"
            "while fast and fast.next:\n"
            "    slow, fast = slow.next, fast.next.next\n"
            "# slow is now at the middle"
        ),
        "pattern2": (
            "# Remove Nth node from end — one pass with gap\n"
            "dummy = ListNode(0, head)\n"
            "left, right = dummy, head\n"
            "for _ in range(n):         # advance right by n steps\n"
            "    right = right.next\n"
            "while right:               # move both until right hits end\n"
            "    left, right = left.next, right.next\n"
            "left.next = left.next.next # delete target\n"
            "return dummy.next"
        ),
        "pitfalls": (
            "• Use a dummy head node to simplify edge cases (empty list, head deletion).\n"
            "• Cycle start: after slow/fast meet, reset one pointer to head, step both by 1.\n"
            "• Reversing in groups: track the prev-tail and connect segments carefully."
        ),
        "time": "O(n)",
        "space": "O(1)",
        "problems": [
            ("Reverse Linked List",         "E"),
            ("Merge Two Sorted Lists",      "E"),
            ("Linked List Cycle",           "E"),
            ("Remove Nth Node From End",    "M"),
            ("Reorder List",                "M"),
            ("LRU Cache",                   "M"),
        ],
        "related": ["Two Pointers", "Stack"],
    },

    # ── 9. Trees ──────────────────────────────────────────────────────────
    {
        "title": "Trees",
        "slug": "Tree",
        "recognize": (
            "hierarchical data, BST property, path sum, depth/height,\n"
            "  lowest common ancestor, serialise/deserialise tree."
        ),
        "diagram": (
            "           4\n"
            "          / \\\n"
            "         2   6\n"
            "        / \\ / \\\n"
            "       1  3 5  7\n"
            "\n"
            "  DFS inorder   (L→N→R): 1 2 3 4 5 6 7  ← sorted for BST\n"
            "  DFS preorder  (N→L→R): 4 2 1 3 6 5 7\n"
            "  DFS postorder (L→R→N): 1 3 2 5 7 6 4\n"
            "  BFS level-order:       4 2 6 1 3 5 7"
        ),
        "when": (
            "Hierarchical data. Use DFS for path problems and subtree queries;\n"
            "  BFS for level-by-level processing or shortest paths."
        ),
        "pattern": (
            "# DFS recursive — max depth\n"
            "def dfs(node):\n"
            "    if not node: return 0\n"
            "    return 1 + max(dfs(node.left), dfs(node.right))\n"
            "\n"
            "# BFS iterative — level order\n"
            "from collections import deque\n"
            "q, res = deque([root]), []\n"
            "while q:\n"
            "    level = []\n"
            "    for _ in range(len(q)):    # snapshot length each level\n"
            "        node = q.popleft()\n"
            "        level.append(node.val)\n"
            "        if node.left:  q.append(node.left)\n"
            "        if node.right: q.append(node.right)\n"
            "    res.append(level)"
        ),
        "pattern2": (
            "# Validate BST — pass bounds down the recursion\n"
            "def valid(node, lo=float('-inf'), hi=float('inf')):\n"
            "    if not node: return True\n"
            "    if not (lo < node.val < hi): return False\n"
            "    return (valid(node.left,  lo, node.val) and\n"
            "            valid(node.right, node.val, hi))\n"
            "\n"
            "# Lowest Common Ancestor (BST)\n"
            "def lca(node, p, q):\n"
            "    if p.val < node.val and q.val < node.val:\n"
            "        return lca(node.left, p, q)\n"
            "    if p.val > node.val and q.val > node.val:\n"
            "        return lca(node.right, p, q)\n"
            "    return node"
        ),
        "pitfalls": (
            "• BST validation: pass lo/hi bounds through recursion, not just checking\n"
            "  the immediate parent — a node's ancestor constraint must hold.\n"
            "• DFS space is O(h); a skewed tree is O(n). Use an explicit stack if risky.\n"
            "• Level-order: snapshot len(q) at the start of each level iteration."
        ),
        "time": "O(n)",
        "space": "O(h)   h = height  (O(n) worst — fully skewed tree)",
        "problems": [
            ("Invert Binary Tree",                    "E"),
            ("Maximum Depth of Binary Tree",           "E"),
            ("Binary Tree Level Order Traversal",      "M"),
            ("Validate Binary Search Tree",            "M"),
            ("Lowest Common Ancestor of a BST",        "M"),
            ("Binary Tree Maximum Path Sum",           "H"),
            ("Serialize and Deserialize Binary Tree",  "H"),
        ],
        "related": ["Graphs", "Dynamic Programming"],
    },

    # ── 10. Tries ─────────────────────────────────────────────────────────
    {
        "title": "Tries",
        "slug": "Trie",
        "recognize": (
            "prefix search, autocomplete, \"starts with\", spell-checking,\n"
            "  word search in a board, grouping words by shared prefix."
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
            "  or grouping words by shared prefixes."
        ),
        "pattern": (
            "class TrieNode:\n"
            "    def __init__(self):\n"
            "        self.children = {}\n"
            "        self.is_end   = False\n"
            "\n"
            "class Trie:\n"
            "    def __init__(self): self.root = TrieNode()\n"
            "\n"
            "    def insert(self, word):\n"
            "        node = self.root\n"
            "        for ch in word:\n"
            "            node = node.children.setdefault(ch, TrieNode())\n"
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
            "        return True"
        ),
        "pattern2": "",
        "pitfalls": (
            "• search() requires is_end=True; starts_with() does not.\n"
            "• For wildcard '.', DFS over all children at that character position.\n"
            "• Array[26] instead of dict is faster but only works for lowercase a-z."
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
    },

    # ── 11. Heap / Priority Queue ─────────────────────────────────────────
    {
        "title": "Heap / Priority Queue",
        "slug": "Heap (Priority Queue)",
        "recognize": (
            "top-K elements, K-th largest/smallest, streaming median,\n"
            "  merge K sorted lists, task scheduling, Dijkstra."
        ),
        "diagram": (
            "  min-heap:       1              max-heap (negate):\n"
            "                / \\                            9\n"
            "               3   2                         / \\\n"
            "              / \\ / \\                        7   8\n"
            "             7  4 5  6\n"
            "\n"
            "  push   O(log n)    pop   O(log n)    peek  O(1)\n"
            "  heapify list in-place  →  O(n)"
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
            "peek = heap[0]\n"
            "\n"
            "# Max-heap: negate values\n"
            "heapq.heappush(heap, -val)\n"
            "largest = -heapq.heappop(heap)\n"
            "\n"
            "# Heapify in-place  O(n)\n"
            "heapq.heapify(arr)\n"
            "\n"
            "# Top K largest  O(n log k)\n"
            "return heapq.nlargest(k, nums)"
        ),
        "pattern2": (
            "# Find Median from Data Stream — two heaps\n"
            "lo = []   # max-heap (negate) — lower half\n"
            "hi = []   # min-heap          — upper half\n"
            "\n"
            "def add_num(num):\n"
            "    heapq.heappush(lo, -num)\n"
            "    heapq.heappush(hi, -heapq.heappop(lo))   # balance\n"
            "    if len(lo) < len(hi):\n"
            "        heapq.heappush(lo, -heapq.heappop(hi))\n"
            "\n"
            "def find_median():\n"
            "    if len(lo) > len(hi): return -lo[0]\n"
            "    return (-lo[0] + hi[0]) / 2"
        ),
        "pitfalls": (
            "• Python heapq is min-heap only — negate values for max-heap.\n"
            "• heap[0] peeks without popping; never index beyond [0] in an unsorted heap.\n"
            "• For (priority, value) tuples, heapq compares the first element, then second."
        ),
        "time": "O(log n) push/pop  /  O(n) heapify  /  O(n log k) top-K",
        "space": "O(k)  for top-K heap",
        "problems": [
            ("Kth Largest Element in an Array",  "M"),
            ("Top K Frequent Elements",          "M"),
            ("K Closest Points to Origin",       "M"),
            ("Task Scheduler",                   "M"),
            ("Merge K Sorted Lists",             "H"),
            ("Find Median from Data Stream",     "H"),
        ],
        "related": ["Binary Search", "Dijkstra"],
    },

    # ── 12. Graphs ────────────────────────────────────────────────────────
    {
        "title": "Graphs",
        "slug": "Graph",
        "recognize": (
            "network traversal, connectivity, cycle detection, \"clone\",\n"
            "  word ladder, friend groups, number of components."
        ),
        "diagram": (
            "  adjacency list:\n"
            "  0: [1, 2]          0 ── 1 ── 3\n"
            "  1: [0, 3]          │\n"
            "  2: [0, 4]          2 ── 4\n"
            "  3: [1]\n"
            "  4: [2]\n"
            "\n"
            "  BFS → queue    shortest path, level order\n"
            "  DFS → stack    connectivity, cycles, components"
        ),
        "when": (
            "Network traversal, connectivity, shortest path (unweighted),\n"
            "  cycle detection, or counting connected components."
        ),
        "pattern": (
            "# BFS — shortest path (unweighted)\n"
            "from collections import deque\n"
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
        "pattern2": (
            "# DFS — connected components + cycle detection (directed)\n"
            "# state: 0=unvisited  1=in-stack  2=done\n"
            "state = [0] * n\n"
            "\n"
            "def dfs(node):\n"
            "    if state[node] == 1: return True   # back edge → cycle\n"
            "    if state[node] == 2: return False\n"
            "    state[node] = 1\n"
            "    for nei in graph[node]:\n"
            "        if dfs(nei): return True\n"
            "    state[node] = 2\n"
            "    return False\n"
            "\n"
            "return any(dfs(i) for i in range(n) if state[i] == 0)"
        ),
        "pitfalls": (
            "• Mark visited BEFORE enqueuing (BFS), not after dequeuing — prevents re-enqueue.\n"
            "• Directed cycle: needs 3 states (unvisited / in-stack / done).\n"
            "• Undirected cycle: track parent to avoid treating the incoming edge as a back edge."
        ),
        "time": "O(V + E)",
        "space": "O(V)",
        "problems": [
            ("Clone Graph",                  "M"),
            ("Course Schedule",              "M"),
            ("Number of Islands",            "M"),
            ("Pacific Atlantic Water Flow",  "M"),
            ("Word Ladder",                  "H"),
            ("Rotting Oranges",              "M"),
        ],
        "related": ["Matrix / Grid", "Union Find", "Topological Sort", "Dijkstra"],
    },

    # ── 13. Matrix / Grid ─────────────────────────────────────────────────
    {
        "title": "Matrix / Grid",
        "slug": "Matrix",
        "recognize": (
            "\"grid\", \"matrix\", \"island\", \"flood fill\", \"neighbors\",\n"
            "  shortest path in 2D space, \"0/1 matrix\", \"walls and gates\"."
        ),
        "diagram": (
            "  4-directional neighbours of (r, c):\n"
            "  DIRS = [(-1,0),(1,0),(0,-1),(0,1)]\n"
            "\n"
            "         (r-1,c)\n"
            "            ↑\n"
            "  (r,c-1) ← (r,c) → (r,c+1)\n"
            "            ↓\n"
            "         (r+1,c)\n"
            "\n"
            "  Multi-source BFS — enqueue ALL sources at distance 0 first."
        ),
        "when": (
            "Shortest path or flood-fill in a 2D grid.\n"
            "  BFS for shortest path; DFS for area/component counting."
        ),
        "pattern": (
            "# BFS shortest path in grid\n"
            "from collections import deque\n"
            "DIRS = [(-1,0),(1,0),(0,-1),(0,1)]\n"
            "rows, cols = len(grid), len(grid[0])\n"
            "visited = {(sr, sc)}\n"
            "q = deque([(sr, sc, 0)])\n"
            "while q:\n"
            "    r, c, dist = q.popleft()\n"
            "    if (r, c) == (er, ec): return dist\n"
            "    for dr, dc in DIRS:\n"
            "        nr, nc = r + dr, c + dc\n"
            "        if (0 <= nr < rows and 0 <= nc < cols\n"
            "                and (nr, nc) not in visited\n"
            "                and grid[nr][nc] != WALL):\n"
            "            visited.add((nr, nc))\n"
            "            q.append((nr, nc, dist + 1))"
        ),
        "pattern2": (
            "# DFS island area — mark visited in-place\n"
            "def dfs(r, c):\n"
            "    if r < 0 or r >= rows or c < 0 or c >= cols: return 0\n"
            "    if grid[r][c] != '1': return 0\n"
            "    grid[r][c] = '0'   # mark visited\n"
            "    return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)\n"
            "\n"
            "count = 0\n"
            "for r in range(rows):\n"
            "    for c in range(cols):\n"
            "        if grid[r][c] == '1':\n"
            "            dfs(r, c)\n"
            "            count += 1"
        ),
        "pitfalls": (
            "• Bounds check: 0 <= nr < rows AND 0 <= nc < cols (both axes).\n"
            "• Multi-source BFS: enqueue ALL sources at distance 0 before the loop starts.\n"
            "• Mark visited when enqueuing, not when dequeuing."
        ),
        "time": "O(m × n)",
        "space": "O(m × n)  visited set  /  O(m×n) recursion stack for DFS",
        "problems": [
            ("Number of Islands",            "M"),
            ("Flood Fill",                   "E"),
            ("Rotting Oranges",              "M"),
            ("01 Matrix",                    "M"),
            ("Pacific Atlantic Water Flow",  "M"),
            ("Word Search",                  "M"),
        ],
        "related": ["Graphs", "Union Find"],
    },

    # ── 14. Union Find ────────────────────────────────────────────────────
    {
        "title": "Union Find",
        "slug": "Union Find",
        "recognize": (
            "\"connected components\", \"same group\", \"merge\", \"friends\",\n"
            "  \"redundant connection\", dynamic connectivity queries."
        ),
        "diagram": (
            "  parent: [0, 1, 2, 3, 4]  (each node is its own root)\n"
            "\n"
            "  union(0,1) → parent[1]=0:   0←1   2   3   4\n"
            "  union(2,3) → parent[3]=2:   0←1   2←3   4\n"
            "  union(0,3) → parent[2]=0:   0←1←(2←3)   4\n"
            "\n"
            "  find(3) with path compression:\n"
            "  3→2→0  then  parent[3]=0, parent[2]=0  (flattened)"
        ),
        "when": (
            "Detecting connected components, merging groups, or checking\n"
            "  whether two nodes are in the same component."
        ),
        "pattern": (
            "class UnionFind:\n"
            "    def __init__(self, n):\n"
            "        self.parent = list(range(n))\n"
            "        self.rank   = [0] * n\n"
            "\n"
            "    def find(self, x):               # path compression\n"
            "        if self.parent[x] != x:\n"
            "            self.parent[x] = self.find(self.parent[x])\n"
            "        return self.parent[x]\n"
            "\n"
            "    def union(self, x, y):           # union by rank\n"
            "        rx, ry = self.find(x), self.find(y)\n"
            "        if rx == ry: return False    # already connected\n"
            "        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx\n"
            "        self.parent[ry] = rx\n"
            "        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1\n"
            "        return True\n"
            "\n"
            "    def connected(self, x, y):\n"
            "        return self.find(x) == self.find(y)"
        ),
        "pattern2": "",
        "pitfalls": (
            "• Path compression alone is O(log n); union by rank is needed for O(α(n)).\n"
            "• union() returns False when already connected — use this for cycle detection.\n"
            "• String nodes: map them to integers with a dict before creating the UF."
        ),
        "time": "O(α(n)) ≈ O(1) per operation  (inverse Ackermann)",
        "space": "O(n)",
        "problems": [
            ("Number of Provinces",              "M"),
            ("Redundant Connection",             "M"),
            ("Accounts Merge",                   "M"),
            ("Graph Valid Tree",                 "M"),
            ("Number of Connected Components",   "M"),
            ("Satisfiability of Equality Eqs",   "M"),
        ],
        "related": ["Graphs", "Matrix / Grid"],
    },

    # ── 15. Topological Sort ──────────────────────────────────────────────
    {
        "title": "Topological Sort",
        "slug": "Topological Sort",
        "recognize": (
            "\"prerequisites\", \"dependency order\", \"build order\",\n"
            "  \"course schedule\", \"alien dictionary\", directed acyclic graph."
        ),
        "diagram": (
            "  DAG:   0 → 1 → 3\n"
            "         ↓       ↑\n"
            "         2 ──────┘\n"
            "\n"
            "  Kahn's BFS — in-degree array:\n"
            "  in-degree: [0, 1, 1, 2]\n"
            "  queue: [0]\n"
            "  → process 0, decrement neighbours → queue [1, 2]\n"
            "  → process 1, decrement 3\n"
            "  → process 2, decrement 3 → in_degree[3]=0, queue [3]\n"
            "  → process 3\n"
            "  order: [0,1,2,3]  |  if len(order) < n → cycle!"
        ),
        "when": (
            "Ordering tasks with dependencies. Detecting cycles in a directed graph.\n"
            "  Only works on DAGs (directed acyclic graphs)."
        ),
        "pattern": (
            "# Kahn's algorithm (BFS + in-degree)\n"
            "from collections import deque\n"
            "in_degree = [0] * n\n"
            "graph     = [[] for _ in range(n)]\n"
            "for u, v in edges:                # u must come before v\n"
            "    graph[u].append(v)\n"
            "    in_degree[v] += 1\n"
            "\n"
            "q = deque(i for i in range(n) if in_degree[i] == 0)\n"
            "order = []\n"
            "while q:\n"
            "    node = q.popleft()\n"
            "    order.append(node)\n"
            "    for nei in graph[node]:\n"
            "        in_degree[nei] -= 1\n"
            "        if in_degree[nei] == 0:\n"
            "            q.append(nei)\n"
            "return order if len(order) == n else []   # [] means cycle"
        ),
        "pattern2": "",
        "pitfalls": (
            "• If result length < n, a cycle exists — return [] or False accordingly.\n"
            "• Edge direction: (prereq, course) means prereq → course.\n"
            "• Kahn's is easiest to implement; DFS topo sort appends in postorder."
        ),
        "time": "O(V + E)",
        "space": "O(V + E)",
        "problems": [
            ("Course Schedule",           "M"),
            ("Course Schedule II",        "M"),
            ("Find All Recipes",          "M"),
            ("Alien Dictionary",          "H"),
            ("Sequence Reconstruction",   "M"),
            ("Minimum Height Trees",      "M"),
        ],
        "related": ["Graphs", "Union Find"],
    },

    # ── 16. Dijkstra ──────────────────────────────────────────────────────
    {
        "title": "Dijkstra",
        "slug": "Dijkstra",
        "recognize": (
            "\"shortest path\", \"minimum cost\", weighted graph,\n"
            "  non-negative edge weights, \"network delay\", \"cheapest flights\"."
        ),
        "diagram": (
            "  Weighted graph  (src = 0):\n"
            "  0 ──4── 1\n"
            "  │       │\n"
            "  2       2\n"
            "  │       │\n"
            "  2 ──1── 3\n"
            "\n"
            "  dist: [0, ∞, ∞, ∞]  heap: [(0,0)]\n"
            "  pop (0,0) → relax: dist[1]=4, dist[2]=2\n"
            "  pop (2,2) → relax: dist[3]=3\n"
            "  pop (3,3) → relax: dist[1]=min(4,5) — no update\n"
            "  pop (4,1) → done\n"
            "  dist: [0, 4, 2, 3]"
        ),
        "when": (
            "Shortest path in a weighted graph with non-negative edge weights.\n"
            "  For negative weights use Bellman-Ford instead."
        ),
        "pattern": (
            "import heapq\n"
            "\n"
            "def dijkstra(graph, src, n):\n"
            "    # graph[u] = [(weight, v), ...]\n"
            "    dist = [float('inf')] * n\n"
            "    dist[src] = 0\n"
            "    heap = [(0, src)]         # (distance, node)\n"
            "    while heap:\n"
            "        d, u = heapq.heappop(heap)\n"
            "        if d > dist[u]: continue   # stale entry — skip\n"
            "        for w, v in graph[u]:\n"
            "            if dist[u] + w < dist[v]:\n"
            "                dist[v] = dist[u] + w\n"
            "                heapq.heappush(heap, (dist[v], v))\n"
            "    return dist"
        ),
        "pattern2": "",
        "pitfalls": (
            "• Always skip stale entries: if d > dist[u]: continue.\n"
            "• Negative weights → Dijkstra gives wrong results; use Bellman-Ford.\n"
            "• K-stops constraint (Cheapest Flights): modified BFS or Bellman-Ford, not Dijkstra."
        ),
        "time": "O((V + E) log V)",
        "space": "O(V + E)",
        "problems": [
            ("Network Delay Time",               "M"),
            ("Path With Minimum Effort",         "M"),
            ("Cheapest Flights Within K Stops",  "M"),
            ("Find the City",                    "M"),
            ("Swim in Rising Water",             "H"),
        ],
        "related": ["Graphs", "Heap / Priority Queue"],
    },

    # ── 17. Backtracking ──────────────────────────────────────────────────
    {
        "title": "Backtracking",
        "slug": "Backtracking",
        "recognize": (
            "\"all combinations\", \"all permutations\", \"all subsets\",\n"
            "  N-Queens, Sudoku, Word Search, Palindrome Partitioning."
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
            "  Constraint-satisfaction (N-Queens, Sudoku, Word Search)."
        ),
        "pattern": (
            "# Subsets / Combinations\n"
            "def backtrack(start, path):\n"
            "    result.append(path[:])           # record a copy\n"
            "    for i in range(start, len(nums)):\n"
            "        path.append(nums[i])          # choose\n"
            "        backtrack(i + 1, path)        # explore\n"
            "        path.pop()                    # unchoose\n"
            "\n"
            "result = []; backtrack(0, []); return result"
        ),
        "pattern2": (
            "# Permutations with duplicates — used[] array\n"
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
            "        used[i] = False"
        ),
        "pitfalls": (
            "• Append path[:] (a copy), not path — path is mutated throughout.\n"
            "• Permutations with duplicates: sort + skip same value when prev not used.\n"
            "• Pruning: add early-exit conditions before recursing to cut dead branches."
        ),
        "time": "O(2ⁿ) subsets   /   O(n!) permutations",
        "space": "O(n)   recursion depth",
        "problems": [
            ("Subsets",                   "M"),
            ("Combination Sum",           "M"),
            ("Permutations",              "M"),
            ("Permutations II",           "M"),
            ("Word Search",               "M"),
            ("Palindrome Partitioning",   "M"),
            ("N-Queens",                  "H"),
        ],
        "related": ["Tries", "Dynamic Programming"],
    },

    # ── 18. Dynamic Programming ───────────────────────────────────────────
    {
        "title": "Dynamic Programming",
        "slug": "Dynamic Programming",
        "recognize": (
            "\"how many ways\", \"minimum cost\", \"maximum profit\",\n"
            "  overlapping subproblems, optimal substructure, \"longest subsequence\"."
        ),
        "diagram": (
            "  Steps to solve any DP problem:\n"
            "  1. Define state:      dp[i] = ?\n"
            "  2. Write transition:  dp[i] = f(dp[i-1], ...)\n"
            "  3. Identify base cases\n"
            "  4. Determine iteration order\n"
            "\n"
            "  Coin Change (unbounded knapsack):\n"
            "  coins=[1,2,5]  amount=6\n"
            "  dp:  [0, 1, 1, 2, 2, 1, 2]   ← dp[6] = 2  (5+1)"
        ),
        "when": (
            "Overlapping subproblems + optimal substructure.\n"
            "  Counting ways, min/max cost, longest subsequences."
        ),
        "pattern": (
            "# Top-down (memoisation) — easiest to write first\n"
            "from functools import cache\n"
            "@cache\n"
            "def dp(i):\n"
            "    if i <= 1: return i              # base case\n"
            "    return dp(i - 1) + dp(i - 2)    # transition\n"
            "\n"
            "# Bottom-up (tabulation)\n"
            "dp = [0] * (n + 1)\n"
            "dp[0], dp[1] = 0, 1\n"
            "for i in range(2, n + 1):\n"
            "    dp[i] = dp[i-1] + dp[i-2]\n"
            "\n"
            "# Space-optimised rolling variables  O(1)\n"
            "a, b = 0, 1\n"
            "for _ in range(2, n + 1):\n"
            "    a, b = b, a + b"
        ),
        "pattern2": (
            "# 0/1 Knapsack — iterate weight in REVERSE\n"
            "dp = [0] * (capacity + 1)\n"
            "for weight, value in items:\n"
            "    for w in range(capacity, weight - 1, -1):  # reverse!\n"
            "        dp[w] = max(dp[w], dp[w - weight] + value)\n"
            "\n"
            "# Longest Common Subsequence (2D DP)\n"
            "m, n = len(s1), len(s2)\n"
            "dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
            "for i in range(1, m + 1):\n"
            "    for j in range(1, n + 1):\n"
            "        if s1[i-1] == s2[j-1]:\n"
            "            dp[i][j] = dp[i-1][j-1] + 1\n"
            "        else:\n"
            "            dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n"
            "return dp[m][n]"
        ),
        "pitfalls": (
            "• 0/1 Knapsack: reverse weight loop so each item is used at most once.\n"
            "  Unbounded (Coin Change): forward loop.\n"
            "• @cache arguments must be hashable — use tuples, not lists.\n"
            "• Base cases are the most common bug source — verify with small inputs."
        ),
        "time": "O(n) 1D   /   O(m × n) 2D   /   O(n × capacity) knapsack",
        "space": "O(n) table  or  O(1) with rolling-array optimisation",
        "problems": [
            ("Climbing Stairs",                     "E"),
            ("House Robber",                        "M"),
            ("Coin Change",                         "M"),
            ("Longest Increasing Subsequence",      "M"),
            ("Longest Common Subsequence",          "M"),
            ("Word Break",                          "M"),
            ("Partition Equal Subset Sum",          "M"),
            ("Edit Distance",                       "M"),
            ("Burst Balloons",                      "H"),
        ],
        "related": ["Backtracking", "Greedy"],
    },

    # ── 19. Greedy ────────────────────────────────────────────────────────
    {
        "title": "Greedy",
        "slug": "Greedy",
        "recognize": (
            "\"minimum number of\", \"maximum coverage\", interval scheduling,\n"
            "  jump games, \"can reach end\", activity selection."
        ),
        "diagram": (
            "  Activity selection — earliest finish first:\n"
            "  A: ─────────\n"
            "  B:      ─────────    ← A chosen (ends first)\n"
            "  C:           ─────   ← C chosen (next after A)\n"
            "  D:                ── ← D chosen\n"
            "       0   3   5   7   9\n"
            "\n"
            "  local optimum at each step  →  global optimum"
        ),
        "when": (
            "Local optimum reliably leads to global optimum.\n"
            "  Interval scheduling, jump games, fractional knapsack."
        ),
        "pattern": (
            "# Jump Game II — minimum jumps to reach end\n"
            "jumps = farthest = end = 0\n"
            "for i in range(len(nums) - 1):\n"
            "    farthest = max(farthest, i + nums[i])\n"
            "    if i == end:           # must take a jump here\n"
            "        jumps += 1\n"
            "        end = farthest\n"
            "return jumps"
        ),
        "pattern2": (
            "# Gas Station — find starting index\n"
            "# Insight: if total gas >= total cost, a solution always exists.\n"
            "total = tank = start = 0\n"
            "for i in range(len(gas)):\n"
            "    diff   = gas[i] - cost[i]\n"
            "    total += diff\n"
            "    tank  += diff\n"
            "    if tank < 0:    # can't reach i+1 from current start\n"
            "        start = i + 1\n"
            "        tank  = 0\n"
            "return start if total >= 0 else -1"
        ),
        "pitfalls": (
            "• Greedy doesn't always work — verify the exchange argument first.\n"
            "• Intervals: sort by END for max non-overlapping; by START for merge.\n"
            "• Jump Game: track farthest reachable index, not just current position."
        ),
        "time": "O(n log n) with sorting   /   O(n) otherwise",
        "space": "O(1)",
        "problems": [
            ("Jump Game",          "M"),
            ("Jump Game II",       "M"),
            ("Gas Station",        "M"),
            ("Merge Intervals",    "M"),
            ("Partition Labels",   "M"),
            ("Hand of Straights",  "M"),
        ],
        "related": ["Dynamic Programming", "Intervals"],
    },

    # ── 20. Intervals ─────────────────────────────────────────────────────
    {
        "title": "Intervals",
        "slug": "Intervals",
        "recognize": (
            "\"overlapping\", \"scheduling\", \"meeting rooms\", \"insert interval\",\n"
            "  \"merge ranges\", \"minimum intervals to remove\"."
        ),
        "diagram": (
            "  Merge overlapping intervals:\n"
            "  input:   [1──3]  [2────5]  [6──8]  [9─10]\n"
            "  sort by start, merge if next.start <= current.end:\n"
            "  output:  [1────────5]      [6──8]  [9─10]\n"
            "\n"
            "  overlap condition:  next.start  <=  current.end"
        ),
        "when": (
            "Scheduling, calendar conflicts, merging ranges,\n"
            "  or finding the minimum coverage / number of rooms needed."
        ),
        "pattern": (
            "# Merge intervals\n"
            "intervals.sort(key=lambda x: x[0])\n"
            "merged = [intervals[0]]\n"
            "for start, end in intervals[1:]:\n"
            "    if start <= merged[-1][1]:           # overlapping\n"
            "        merged[-1][1] = max(merged[-1][1], end)\n"
            "    else:\n"
            "        merged.append([start, end])\n"
            "return merged"
        ),
        "pattern2": (
            "# Meeting Rooms II — minimum rooms (heap of end times)\n"
            "import heapq\n"
            "intervals.sort(key=lambda x: x[0])\n"
            "heap = []   # end times of ongoing meetings\n"
            "for start, end in intervals:\n"
            "    if heap and heap[0] <= start:\n"
            "        heapq.heapreplace(heap, end)  # reuse a room\n"
            "    else:\n"
            "        heapq.heappush(heap, end)     # new room needed\n"
            "return len(heap)"
        ),
        "pitfalls": (
            "• Always sort by start time first.\n"
            "• Merge: use max(current.end, next.end) — next may be fully contained.\n"
            "• Non-overlapping (remove minimum): sort by end, greedy keep earliest-ending."
        ),
        "time": "O(n log n)",
        "space": "O(n)",
        "problems": [
            ("Merge Intervals",                        "M"),
            ("Insert Interval",                        "M"),
            ("Non-overlapping Intervals",              "M"),
            ("Meeting Rooms",                          "E"),
            ("Meeting Rooms II",                       "M"),
            ("Minimum Interval to Include Each Query", "H"),
        ],
        "related": ["Greedy", "Heap / Priority Queue"],
    },

    # ── 21. Bit Manipulation ──────────────────────────────────────────────
    {
        "title": "Bit Manipulation",
        "slug": "Bit Manipulation",
        "recognize": (
            "\"single number\", \"unique among duplicates\", \"count bits\",\n"
            "  \"missing number\", \"sum without +\", bitmask DP over subsets."
        ),
        "diagram": (
            "  AND  &    OR  |    XOR  ^    NOT  ~    SHIFT  <<  >>\n"
            "   1&1=1   1|0=1   1^1=0   ~1=-2   2<<1=4\n"
            "   1&0=0   0|0=0   1^0=1   ~0=-1   8>>1=4\n"
            "\n"
            "  Common tricks:\n"
            "  n & (n-1)    →  clear lowest set bit\n"
            "  n & (-n)     →  isolate lowest set bit\n"
            "  a ^ b ^ b    →  a   (XOR cancels duplicate pairs)\n"
            "  (i >> k) & 1 →  k-th bit of i"
        ),
        "when": (
            "Binary representations, bitmask flags, counting set bits,\n"
            "  or finding unique elements among duplicates."
        ),
        "pattern": (
            "# Count set bits — Brian Kernighan  O(k)\n"
            "count = 0\n"
            "while n:\n"
            "    n &= n - 1       # clear lowest set bit\n"
            "    count += 1\n"
            "\n"
            "# Find single number (XOR cancels all duplicates)\n"
            "result = 0\n"
            "for num in nums:\n"
            "    result ^= num\n"
            "return result\n"
            "\n"
            "# Missing number\n"
            "result = len(nums)\n"
            "for i, num in enumerate(nums):\n"
            "    result ^= i ^ num\n"
            "return result"
        ),
        "pattern2": (
            "# Bitmask DP — enumerate all 2^n subsets\n"
            "n = len(items)\n"
            "dp = [float('inf')] * (1 << n)\n"
            "dp[0] = 0\n"
            "for mask in range(1 << n):\n"
            "    for i in range(n):\n"
            "        if mask & (1 << i):           # item i is in this subset\n"
            "            prev = mask ^ (1 << i)    # mask without item i\n"
            "            dp[mask] = min(dp[mask], dp[prev] + cost[i])"
        ),
        "pitfalls": (
            "• Python ~n = -(n+1), not a bitwise flip to 0/1 — use (n ^ mask) instead.\n"
            "• Bitmask DP: 2^n states — only feasible for n ≤ 20.\n"
            "• Two unique numbers: XOR all, then split by a differing bit to separate them."
        ),
        "time": "O(1) bitwise ops   /   O(log n) per-bit loops   /   O(2ⁿ) bitmask DP",
        "space": "O(1)   (O(2ⁿ) for bitmask DP)",
        "problems": [
            ("Single Number",          "E"),
            ("Number of 1 Bits",       "E"),
            ("Missing Number",         "E"),
            ("Counting Bits",          "E"),
            ("Reverse Bits",           "E"),
            ("Sum of Two Integers",    "M"),
        ],
        "related": ["Dynamic Programming"],
    },

    # ── 22. Math Patterns ─────────────────────────────────────────────────
    {
        "title": "Math Patterns",
        "slug": "Math",
        "recognize": (
            "\"prime\", \"GCD\", \"LCM\", \"power\", \"modulo\", \"factorial\",\n"
            "  \"digit\", \"base conversion\", \"count primes\", \"happy number\"."
        ),
        "diagram": (
            "  GCD (Euclidean):  gcd(a,b) = gcd(b, a%b)  until b=0\n"
            "  gcd(48,18) → gcd(18,12) → gcd(12,6) → gcd(6,0) = 6\n"
            "\n"
            "  Fast Power (binary exponentiation):\n"
            "  2^13 = 2^8 × 2^4 × 2^1   (13 = 1101 in binary)\n"
            "  O(log n) multiplications\n"
            "\n"
            "  Sieve of Eratosthenes  O(n log log n):\n"
            "  mark every multiple of p (p*p, p*p+p, ...) as composite"
        ),
        "when": (
            "Number theory problems: primes, GCD, modular arithmetic,\n"
            "  combinatorics (nCr mod p), or digit manipulation."
        ),
        "pattern": (
            "from math import gcd\n"
            "\n"
            "# Fast power  O(log exp)\n"
            "def fast_pow(base, exp, mod):\n"
            "    result = 1\n"
            "    base %= mod\n"
            "    while exp > 0:\n"
            "        if exp & 1:\n"
            "            result = result * base % mod\n"
            "        base = base * base % mod\n"
            "        exp >>= 1\n"
            "    return result\n"
            "# or simply: pow(base, exp, mod)  — Python built-in\n"
            "\n"
            "# Sieve of Eratosthenes\n"
            "def count_primes(n):\n"
            "    sieve = [True] * n\n"
            "    sieve[0] = sieve[1] = False\n"
            "    for p in range(2, int(n**0.5) + 1):\n"
            "        if sieve[p]:\n"
            "            for m in range(p * p, n, p):\n"
            "                sieve[m] = False\n"
            "    return sum(sieve)"
        ),
        "pattern2": (
            "# Happy Number — cycle detection via fast/slow pointers\n"
            "def digit_square_sum(n):\n"
            "    s = 0\n"
            "    while n:\n"
            "        n, d = divmod(n, 10)\n"
            "        s += d * d\n"
            "    return s\n"
            "\n"
            "slow = fast = n\n"
            "while True:\n"
            "    slow = digit_square_sum(slow)\n"
            "    fast = digit_square_sum(digit_square_sum(fast))\n"
            "    if slow == fast:\n"
            "        return slow == 1"
        ),
        "pitfalls": (
            "• Apply mod after every multiplication: result = result * base % mod.\n"
            "• Sieve: start marking from p*p (not 2*p) — smaller multiples already marked.\n"
            "• Use Python's built-in pow(base, exp, mod) — it is an optimised fast power."
        ),
        "time": "O(log n) GCD / fast-pow   /   O(n log log n) sieve",
        "space": "O(1) math ops   /   O(n) sieve",
        "problems": [
            ("Count Primes",             "M"),
            ("Happy Number",             "E"),
            ("Pow(x, n)",                "M"),
            ("Reverse Integer",          "M"),
            ("Excel Sheet Column Title", "E"),
            ("Sqrt(x)",                  "E"),
        ],
        "related": ["Bit Manipulation", "Dynamic Programming"],
    },
]


# ── Content renderer ───────────────────────────────────────────────────────────

def _render_topic(topic: dict, note: str) -> str:
    """Build a Rich-markup string for the right panel."""

    # ── Pattern Selector (special layout) ───────────────────────────────
    if topic["slug"] == "_selector":
        lines: list[str] = [
            f"[bold {FIRE}]━━━  {topic['title']}  ━━━[/bold {FIRE}]",
            "",
            f"[{GOLD}]How to pick a pattern[/{GOLD}]",
            f"[dim]{'─' * 50}[/dim]",
        ]
        for ln in _esc(topic["diagram"]).split("\n"):
            lines.append(f"  {ln}")
        lines += [
            f"[dim]{'─' * 50}[/dim]",
            "",
            f"  [{DIM}]{_esc(topic['when'])}[/{DIM}]",
        ]
        return "\n".join(lines)

    title    = topic["title"]
    diagram  = _esc(topic.get("diagram", ""))
    when     = _esc(topic.get("when", ""))
    pattern  = _esc(topic.get("pattern", ""))
    pattern2 = _esc(topic.get("pattern2", ""))
    t_val    = _esc(topic.get("time", ""))
    s_val    = _esc(topic.get("space", ""))
    recognize = _esc(topic.get("recognize", ""))
    pitfalls  = _esc(topic.get("pitfalls", ""))
    related   = topic.get("related", [])

    lines: list[str] = [
        f"[bold {FIRE}]━━━  {title}  ━━━[/bold {FIRE}]",
        "",
    ]

    # Recognise
    if recognize:
        lines.append(f"[{GOLD}]Recognise by[/{GOLD}]")
        for ln in recognize.split("\n"):
            lines.append(f"  {ln}")
        lines.append("")

    # Diagram
    lines += [
        f"[{GOLD}]Diagram[/{GOLD}]",
        f"[dim]{'─' * 44}[/dim]",
    ]
    lines += [f"  {ln}" for ln in diagram.split("\n")]
    lines += [
        f"[dim]{'─' * 44}[/dim]",
        "",
    ]

    # When to use
    lines.append(f"[{GOLD}]When to use[/{GOLD}]")
    for ln in when.split("\n"):
        lines.append(f"  {ln}")
    lines.append("")

    # Pattern
    if pattern:
        lines += [
            f"[{GOLD}]Pattern[/{GOLD}]",
            f"[dim]─── python {'─' * 33}[/dim]",
        ]
        lines += [f"  {ln}" for ln in pattern.split("\n")]
        lines += [
            f"[dim]{'─' * 44}[/dim]",
            "",
        ]

    # Pattern variant
    if pattern2:
        lines += [
            f"[{GOLD}]Pattern — Variant[/{GOLD}]",
            f"[dim]─── python {'─' * 33}[/dim]",
        ]
        lines += [f"  {ln}" for ln in pattern2.split("\n")]
        lines += [
            f"[dim]{'─' * 44}[/dim]",
            "",
        ]

    # Complexity
    if t_val or s_val:
        lines.append(f"[{GOLD}]Complexity[/{GOLD}]")
        if t_val:
            lines.append(f"  Time    [{AMBER}]{t_val}[/{AMBER}]")
        if s_val:
            lines.append(f"  Space   [{AMBER}]{s_val}[/{AMBER}]")
        lines.append("")

    # Pitfalls
    if pitfalls:
        lines.append(f"[{GOLD}]Pitfalls[/{GOLD}]")
        for ln in pitfalls.split("\n"):
            lines.append(f"  [{RED}]{ln}[/{RED}]")
        lines.append("")

    # Classic Problems
    if topic.get("problems"):
        lines.append(f"[{GOLD}]Classic Problems[/{GOLD}]")
        for item in topic["problems"]:
            if isinstance(item, tuple):
                name, diff = item
                dc = _DIFF_COLOR.get(diff, DIM)
                dl = _DIFF_LABEL.get(diff, diff)
                lines.append(
                    f"  [{DIM}]•[/{DIM}] {_esc(name)}  [{dc}][{dl}][/{dc}]"
                )
            else:
                lines.append(f"  [{DIM}]•[/{DIM}] {_esc(str(item))}")
        lines.append("")

    # Related Topics
    if related:
        lines.append(f"[{GOLD}]Related Topics[/{GOLD}]")
        lines.append(
            "  " + "  ·  ".join(f"[{EMBER}]{r}[/{EMBER}]" for r in related)
        )
        lines.append("")

    # Notes
    if note.strip():
        lines.append(f"[{GOLD}]My Notes[/{GOLD}]")
        for note_line in note.strip().split("\n"):
            lines.append(f"  {_esc(note_line)}")
    else:
        lines.append(
            f"[{DIM}]No notes yet — press [bold]N[/bold] to add one.[/{DIM}]"
        )

    return "\n".join(lines)


# ── Screen ─────────────────────────────────────────────────────────────────────

class ReferenceGuideScreen(BaseScreen):
    """Playbook mode — browse algorithm topics, add notes, and export to DOCX."""

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
            scroll = self.query_one("#ref-content-scroll", VerticalScroll)
            scroll.scroll_home(animate=False)
        except Exception:
            pass

    # ── Actions ─────────────────────────────────────────────────────────

    def action_explain_more(self) -> None:
        """Open an AI session explaining the current topic in depth."""
        from ...problem_loader import Problem
        from .agent_session import AgentSessionScreen

        topic = TOPICS[self._current_idx]

        # Build a flat list of problem names regardless of tuple/str format
        prob_names = [
            (p[0] if isinstance(p, tuple) else p) for p in topic.get("problems", [])
        ]

        synthetic = Problem(
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
                + "\n".join(f"- {p}" for p in prob_names)
            ),
            topics=[topic["slug"]],
        )
        self.app.push_screen(AgentSessionScreen(synthetic, mode="learn"))

    def action_practice(self) -> None:
        """Open problem list pre-filtered to the current topic."""
        from .problem_list import ProblemListScreen
        topic = TOPICS[self._current_idx]
        self.app.push_screen(ProblemListScreen(mode="learn", initial_topic=topic["slug"]))

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
