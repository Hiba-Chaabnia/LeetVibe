from __future__ import annotations

TOPIC: dict = {
    "title": "Cyclic Sort",
    "slug": "Cyclic Sort",
    "recognize": (
        "Array of integers in range [1..n] or [0..n], find missing number, find all duplicates,\n"
        "first missing positive, find corrupt pair.\n"
        "Keywords: n integers in a known 1..n range, O(1) extra space, no hash set allowed."
    ),
    "intuition": (
        "• If nums holds exactly the values [1..n] (or [0..n-1]), each value's correct index is\n"
        "  known ahead of time (value v belongs at index v-1) — so you can sort by placement, not comparison.\n"
        "• Every swap puts at least one element into its final position, so the array converges in O(n)\n"
        "  swaps total — no O(n log n) comparison sort needed.\n"
        "• Once sorted this way, any index i where nums[i] != i+1 exposes a missing or duplicate value\n"
        "  in a single O(n) pass — the array becomes its own hash set."
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
    "variants": (
        "• Find the Missing Number [0..n] — one value missing; scan for the index that doesn't match.\n"
        "• Find All Missing Numbers — same idea, collect every mismatched index.\n"
        "• Find All Duplicates — after sort, nums[i] != i+1 exposes the duplicate value itself.\n"
        "• Find the Duplicate Number (values not distinct) — cyclic sort still works, or use Floyd's\n"
        "  cycle detection (see Fast & Slow Pointers) for the no-mutation constraint.\n"
        "• First Missing Positive — ignore values outside [1..n]; they can never be the answer.\n"
        "• Find the Corrupt Pair (one missing + one duplicate) — single pass after sort finds both."
    ),
    "pitfalls": (
        "• Only advance i when nums[i] is already correct — otherwise keep swapping at the same i.\n"
        "• Duplicates loop forever if nums[i] == nums[j] and neither is placed — guard with\n"
        "  nums[i] != nums[j] before swapping.\n"
        "• Out-of-range values (First Missing Positive): guard with 1 <= nums[i] <= n before swapping."
    ),
    "edge_cases": (
        "• Empty array — First Missing Positive should return 1 immediately.\n"
        "• All values already correct (nums == [1,2,...,n]) — while loop advances i every time, no swaps.\n"
        "• All duplicates of one value — cyclic sort settles after n-1 no-op comparisons; still O(n).\n"
        "• Values outside [1..n] mixed in — must be skipped by the range guard or they corrupt indices."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Arrays & Hashing    │ Values NOT restricted to [1..n]? → hash set, O(n)    │\n"
        "│ (hash set)          │ space. Values ARE exactly [1..n]? → Cyclic Sort,     │\n"
        "│                     │ O(1) space using the array itself as a lookup table. │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you solve Find the Duplicate Number without modifying the array?\n"
        "• The array is read-only — how does that change your approach?\n"
        "• Can you find all missing AND all duplicate numbers in one pass?\n"
        "• Why can't you use this trick if values aren't bounded to a known range?"
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
