from __future__ import annotations

TOPIC: dict = {
    "title": "Binary Search",
    "slug": "Binary Search",
    "recognize": (
        "Sorted array, or any space where a condition flips False → True.\n"
        "Keywords: O(log n) required, 'minimum valid answer', 'maximum valid answer'.\n"
        "If you can write a monotonic yes/no check on an answer — binary search it."
    ),
    "intuition": (
        "• Your condition splits the space: NO NO NO YES YES YES.\n"
        "  Binary search finds the boundary by halving candidates each step.\n"
        "• Once the condition flips, it never flips back — that's what makes it work.\n"
        "• Exact match: converge on the value. Boundary: converge on the edge."
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
    "patterns": [
        {
            "name": "Find exact value",
            "code": (
                "left, right = 0, len(arr) - 1\n"
                "while left <= right:\n"
                "    mid = left + (right - left) // 2   # avoids overflow\n"
                "    if   arr[mid] == target:  return mid\n"
                "    elif arr[mid] <  target:  left  = mid + 1\n"
                "    else:                     right = mid - 1\n"
                "return -1"
            ),
        },
        {
            "name": "Smallest valid answer (binary search on answer space)",
            "code": (
                "left, right = lo, hi          # define the answer range\n"
                "while left < right:           # converges to smallest valid\n"
                "    mid = (left + right) // 2\n"
                "    if feasible(mid):         # monotonic: once True, stays True\n"
                "        right = mid           # mid could be the answer\n"
                "    else:\n"
                "        left = mid + 1\n"
                "return left\n"
                "\n"
                "# Float answer space (e.g. Minimize Max Distance to Gas Station)\n"
                "lo, hi = 0.0, max_possible\n"
                "for _ in range(100):          # ~100 iterations → 1e-30 precision\n"
                "    mid = (lo + hi) / 2\n"
                "    if feasible(mid):\n"
                "        hi = mid\n"
                "    else:\n"
                "        lo = mid\n"
                "return lo"
            ),
        },
    ],
    "variants": (
        "• Exact value — left <= right; return mid on match, -1 if not found.\n"
        "• First True (smallest valid) — left < right; feasible → right=mid; else left=mid+1.\n"
        "• Last True (largest valid) — feasible → left=mid; else right=mid-1; mid=(l+r+1)//2.\n"
        "• Rotated sorted array — detect sorted half by comparing arr[mid] to arr[left].\n"
        "• Float answer space — 100 fixed iterations, not a while loop.\n"
        "• 2D matrix — treat as 1D; map mid → (mid//cols, mid%cols).\n"
        "• bisect module — bisect_left(arr, x) for leftmost insert position; bisect_right for rightmost."
    ),
    "pitfalls": (
        "• Exact search: left <= right. Boundary search: left < right. Don't mix them.\n"
        "• Boundary: set right=mid (not mid-1) when feasible is True.\n"
        "• Largest valid: use mid=(left+right+1)//2 to avoid infinite loop on 2-element range.\n"
        "• Float space: fixed 100 iterations — eps-based loop is slow when lo/hi are large."
    ),
    "edge_cases": (
        "• Empty array — left > right immediately; return -1.\n"
        "• Rotated + duplicates — arr[left]==arr[mid] breaks sorted-half detection; shrink left by 1.\n"
        "• All elements identical — loop still terminates; exact match returns on first check."
    ),
    "confusion": (
        "┌─────────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with     │ Distinguishing question                               │\n"
        "├─────────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Two Pointers            │ Searching for a value in a sorted structure? → BS.    │\n"
        "│                         │ Moving two indices toward each other for a pair? → TP │\n"
        "├─────────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Linear / sliding window │ Is the answer space monotonic? Yes → BS.              │\n"
        "│                         │ No monotonicity? You need a different approach.       │\n"
        "└─────────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you find the first and last position of a target in O(log n)?\n"
        "• The array is sorted but rotated — how does binary search change?\n"
        "• Your feasible() runs in O(n) — what's the overall complexity?\n"
        "• How would you binary search a 2D sorted matrix?"
    ),
    "time": "O(log n)",
    "space": "O(1)",
    "problems": [
        ("Binary Search",                        "E"),
        ("Search in Rotated Sorted Array",        "M"),
        ("Find Minimum in Rotated Sorted Array",  "M"),
        ("Koko Eating Bananas",                   "M"),
        ("Time Based Key-Value Store",            "M"),
        ("Minimize Max Distance to Gas Station",  "H"),
        ("Median of Two Sorted Arrays",           "H"),
    ],
    "related": ["Two Pointers", "Heap / Priority Queue", "Modified Binary Search", "Ordered Set / SortedList"],
}
