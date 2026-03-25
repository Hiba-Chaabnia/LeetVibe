from __future__ import annotations

TOPIC: dict = {
    "title": "Monotonic Stack",
    "slug": "Monotonic Stack",
    "recognize": (
        "next greater element, next smaller, previous larger,\n"
        "daily temperatures, histogram areas, stock span."
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
        "larger or smaller. Histogram-area problems use a variation."
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
        ("Online Stock Span",               "M"),
        ("Car Fleet",                       "M"),
        ("Sum of Subarray Minimums",        "M"),
        ("Largest Rectangle in Histogram",  "H"),
        ("Trapping Rain Water",             "M"),
    ],
    "related": ["Stack", "Sliding Window"],
}
