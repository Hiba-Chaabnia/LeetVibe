from __future__ import annotations

TOPIC: dict = {
    "title": "Monotonic Stack",
    "slug": "Monotonic Stack",
    "recognize": (
        "Next greater element, next smaller, previous larger, daily temperatures, histogram areas, stock span.\n"
        "Signal: 'for each element, find the nearest element satisfying a comparison' — one pass, O(n)."
    ),
    "intuition": (
        "• Any stack element smaller than the new arrival can never be the next-greater for any future element — pop it now.\n"
        "• Each element is pushed once and popped at most once — O(n) total regardless of input.\n"
        "• Elements remaining at the end have no answer — set them to -1 (or 0 for some problems)."
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
    "patterns": [
        {
            "name": "Next Greater Element — store indices in stack",
            "code": (
                "res = [-1] * len(arr)\n"
                "stack = []         # indices, not values\n"
                "for i in range(len(arr)):\n"
                "    while stack and arr[i] > arr[stack[-1]]:\n"
                "        idx = stack.pop()\n"
                "        res[idx] = arr[i]  # arr[i] is the next greater\n"
                "    stack.append(i)\n"
                "return res"
            ),
        },
        {
            "name": "Largest Rectangle in Histogram",
            "code": (
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
        },
    ],
    "variants": (
        "• Next greater element (left→right) — decreasing stack; pop when new > top.\n"
        "• Next smaller element — increasing stack; pop when new < top.\n"
        "• Previous greater element — traverse right→left with decreasing stack.\n"
        "• Circular array (Next Greater Element II) — traverse 2n with i % n; second pass fills unresolved.\n"
        "• Largest Rectangle in Histogram — augmented stack with (start, height); width = i - stored start.\n"
        "• Trapping Rain Water — two-pointer (O(1) space) or stack-based (O(n) space).\n"
        "• Sum of Subarray Minimums — find left/right boundaries with monotonic stack; count subarrays per element."
    ),
    "pitfalls": (
        "• Decreasing stack → next greater; increasing stack → next smaller.\n"
        "• Store INDICES (not values) — you need indices to compute span/width.\n"
        "• After the loop, elements left on the stack have no answer — set them to -1."
    ),
    "edge_cases": (
        "• Empty array — loop doesn't run; return [].\n"
        "• Strictly decreasing array — everything pushed, nothing popped; all answers -1.\n"
        "• All identical elements — strict < means identicals are NOT popped; verify strict vs non-strict.\n"
        "• Circular array — initialise res to -1; second pass only updates elements still on the stack."
    ),
    "confusion": (
        "┌─────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                             │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Monotonic Queue     │ Sliding window with an expiry condition? → Queue.   │\n"
        "│                     │ Next/previous boundary without a window? → Stack.   │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Two Pointers        │ Searching for a pair from both ends? → Two Ptrs.    │\n"
        "│                     │ Nearest element with a comparison condition at each │\n"
        "│                     │ position? → Monotonic Stack.                        │\n"
        "└─────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What if the array is circular (Next Greater Element II)?\n"
        "• How do you find the PREVIOUS greater element instead of next?\n"
        "• Trapping Rain Water — explain the stack-based approach vs two-pointer."
    ),
    "time": "O(n)  — each element pushed and popped at most once",
    "space": "O(n)",
    "problems": [
        ("Daily Temperatures",              "M"),
        ("Next Greater Element I",          "E"),
        ("Online Stock Span",               "M"),
        ("Car Fleet",                       "M"),
        ("Sum of Subarray Minimums",        "M"),
        ("Largest Rectangle in Histogram",  "H"),
        ("Trapping Rain Water",             "M"),
    ],
    "related": ["Stack", "Sliding Window"],
}
