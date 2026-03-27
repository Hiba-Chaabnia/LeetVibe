from __future__ import annotations

TOPIC: dict = {
    "title": "Two Pointers",
    "slug": "Two Pointers",
    "recognize": (
        "Sorted array + find pair/triplet, palindrome check, merge two sorted arrays,\n"
        "remove duplicates in-place.\n"
        "Keywords: sorted (or sortable) input, looking for a PAIR, not a contiguous run."
    ),
    "intuition": (
        "• On a sorted array, moving left forward strictly increases the sum, and moving right\n"
        "  backward strictly decreases it — that monotonicity means you never need to re-check a\n"
        "  pair once you've moved past it, giving O(n) instead of O(n²).\n"
        "• Each pointer moves at most n times total, so even though it looks like nested iteration\n"
        "  conceptually, the two pointers together do O(n) work, not O(n²).\n"
        "• In-place write-pointer patterns (remove duplicates) work because the write position\n"
        "  never overtakes the read position — you're always writing into a cell you've already read."
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
    "patterns": [
        {
            "name": "Two Sum II (Opposite Ends)",
            "code": (
                "left, right = 0, len(arr) - 1\n"
                "while left < right:\n"
                "    s = arr[left] + arr[right]\n"
                "    if   s == target:  return [left + 1, right + 1]\n"
                "    elif s <  target:  left  += 1\n"
                "    else:              right -= 1"
            ),
        },
        {
            "name": "3Sum (Fix + Two-Pointer)",
            "code": (
                "nums.sort()\n"
                "res = []\n"
                "for i in range(len(nums) - 2):\n"
                "    if i > 0 and nums[i] == nums[i - 1]: continue  # skip dupe\n"
                "    l, r = i + 1, len(nums) - 1\n"
                "    while l < r:\n"
                "        s = nums[i] + nums[l] + nums[r]\n"
                "        if   s < 0: l += 1\n"
                "        elif s > 0: r -= 1\n"
                "        else:\n"
                "            res.append([nums[i], nums[l], nums[r]])\n"
                "            l += 1; r -= 1\n"
                "            # skip dupes ONLY after a match — skipping on every\n"
                "            # iteration can jump past valid triplets\n"
                "            while l < r and nums[l] == nums[l - 1]: l += 1\n"
                "            while l < r and nums[r] == nums[r + 1]: r -= 1"
            ),
        },
        {
            "name": "Remove Duplicates In-Place",
            "code": (
                "# k points to the next position to write a new unique value\n"
                "if not nums: return 0\n"
                "k = 1\n"
                "for i in range(1, len(nums)):\n"
                "    if nums[i] != nums[i - 1]:   # new unique value found\n"
                "        nums[k] = nums[i]\n"
                "        k += 1\n"
                "return k  # first k elements are the deduplicated array"
            ),
        },
        {
            "name": "Allow Up to K Duplicates",
            "code": (
                "k = 0\n"
                "for num in nums:\n"
                "    if k < 2 or nums[k - 2] != num:  # safe to write\n"
                "        nums[k] = num\n"
                "        k += 1\n"
                "return k"
            ),
        },
    ],
    "variants": (
        "• Opposite-ends convergence (Two Sum II, Container With Most Water) — left/right close in\n"
        "  based on a comparison against target.\n"
        "• Fix-one + two-pointer (3Sum, 4Sum) — outer loop fixes k-2 elements, inner two pointers\n"
        "  solve the remaining pair.\n"
        "• Same-direction read/write pointers (Remove Duplicates, Move Zeroes) — slow pointer marks\n"
        "  the next write position, fast pointer scans ahead.\n"
        "• Merge two sorted arrays/lists — one pointer per array, advance whichever is smaller.\n"
        "• Trapping Rain Water — two pointers + running max-from-each-side, no extra array needed."
    ),
    "pitfalls": (
        "• 3Sum: skip duplicate values at i, l, r to avoid duplicate triplets.\n"
        "• Array must be sorted first — don't forget nums.sort().\n"
        "• Loop condition is left < right (strict), not <=.\n"
        "• Write-pointer: compare nums[i] with nums[i-1] (sorted input), not nums[k-1], so you\n"
        "  always move past all duplicates before deciding to write."
    ),
    "edge_cases": (
        "• Array length < 2 — pair-finding patterns have no valid answer; guard before the loop.\n"
        "• All elements identical — 3Sum's duplicate-skip logic must still find one valid triplet.\n"
        "• Target unreachable — opposite-ends loop terminates with left >= right and no match.\n"
        "• Already deduplicated input — remove-duplicates write pointer just copies every element."
    ),
    "confusion": (
        "┌─────────────────────┬────────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                                │\n"
        "├─────────────────────┼────────────────────────────────────────────────────────┤\n"
        "│ Sliding Window      │ Need a fixed PAIR of elements (not necessarily         │\n"
        "│                     │ adjacent) from a sorted structure? → Two Pointers.     │\n"
        "│                     │ Need a CONTIGUOUS run satisfying a size/sum condition? │\n"
        "│                     │ → Sliding Window.                                      │\n"
        "└─────────────────────┴────────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• 3Sum: how would you extend this to 4Sum or general k-Sum?\n"
        "• What if the array isn't sorted — is sorting first always worth the O(n log n) cost?\n"
        "• Container With Most Water: why does moving the shorter wall always work as the greedy move?\n"
        "• Can you solve Two Sum II without extra space if the array is a linked list instead?"
    ),
    "time": "O(n) pair  /  O(n²) triplet",
    "space": "O(1)  (excluding output)",
    "problems": [
        ("Two Sum II",                 "M"),
        ("3Sum",                       "M"),
        ("Container With Most Water",  "M"),
        ("Trapping Rain Water",        "M"),
    ],
    "related": ["Sliding Window", "Binary Search", "Fast & Slow Pointers"],
}
