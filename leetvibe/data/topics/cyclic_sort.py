from __future__ import annotations

TOPIC: dict = {
    "title": "Cyclic Sort",
    "slug": "Cyclic Sort",
    "recognize": (
        "array of integers in range [1..n] or [0..n], find missing number,\n"
        "find all duplicates, first missing positive, find corrupt pair."
    ),
    "diagram": (
        "  Place each number at its correct index:  nums[i] should be i+1\n"
        "\n"
        "  arr = [3, 1, 5, 4, 2]\n"
        "  i=0: nums[0]=3 → swap with nums[2]:  [5, 1, 3, 4, 2]\n"
        "  i=0: nums[0]=5 → swap with nums[4]:  [2, 1, 3, 4, 5]\n"
        "  i=0: nums[0]=2 → swap with nums[1]:  [1, 2, 3, 4, 5]  ✓\n"
        "  i=1: nums[1]=2 already correct        advance i\n"
        "  ...\n"
        "  Sorted!  O(n) — each swap moves at least one element to its place."
    ),
    "when": (
        "Input is n integers in a known range like [1..n] or [0..n].\n"
        "Goal is to find missing, duplicate, or misplaced values\n"
        "in O(n) time and O(1) space without a hash set."
    ),
    "patterns": [
        {
            "name": "Cyclic Sort — place every number at nums[i]-1",
            "code": (
                "i = 0\n"
                "while i < len(nums):\n"
                "    j = nums[i] - 1              # correct index for nums[i]\n"
                "    if nums[i] != nums[j]:       # not in the right place\n"
                "        nums[i], nums[j] = nums[j], nums[i]\n"
                "    else:\n"
                "        i += 1                   # already correct, advance\n"
                "\n"
                "# After sort: find missing numbers\n"
                "missing = []\n"
                "for i, num in enumerate(nums):\n"
                "    if num != i + 1:\n"
                "        missing.append(i + 1)\n"
                "return missing"
            ),
        },
        {
            "name": "First Missing Positive — numbers outside [1..n] are irrelevant",
            "code": (
                "n = len(nums)\n"
                "i = 0\n"
                "while i < n:\n"
                "    j = nums[i] - 1\n"
                "    if 1 <= nums[i] <= n and nums[i] != nums[j]:\n"
                "        nums[i], nums[j] = nums[j], nums[i]\n"
                "    else:\n"
                "        i += 1\n"
                "\n"
                "for i in range(n):\n"
                "    if nums[i] != i + 1:\n"
                "        return i + 1\n"
                "return n + 1   # all [1..n] present, answer is n+1\n"
                "\n"
                "# Find all duplicates — after cyclic sort, nums[i] != i+1 → duplicate\n"
                "duplicates = []\n"
                "for i in range(len(nums)):\n"
                "    if nums[i] != i + 1:\n"
                "        duplicates.append(nums[i])\n"
                "return duplicates"
            ),
        },
    ],
    "pitfalls": (
        "• Termination condition: only advance i when nums[i] is already correct;\n"
        "  otherwise keep swapping in-place at the same i until it settles.\n"
        "• Duplicates loop forever if nums[i] == nums[j] and neither is at the\n"
        "  correct index — check nums[i] != nums[j] before swapping.\n"
        "• Out-of-range values (e.g. First Missing Positive): guard with\n"
        "  1 <= nums[i] <= n before attempting the swap."
    ),
    "time": "O(n)  — each element is swapped at most once",
    "space": "O(1)",
    "problems": [
        ("Missing Number",              "E"),
        ("Find All Duplicates",         "M"),
        ("Find All Numbers Disappeared","M"),
        ("First Missing Positive",      "H"),
        ("Find the Corrupt Pair",       "E"),
        ("Find the Duplicate Number",   "M"),
    ],
    "related": ["Arrays & Hashing", "Fast & Slow Pointers", "Bit Manipulation"],
}
