from __future__ import annotations

TOPIC: dict = {
    "title": "Two Pointers",
    "slug": "Two Pointers",
    "recognize": (
        "sorted array + find pair/triplet, palindrome check,\n"
        "merge two sorted arrays, remove duplicates in-place."
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
        "satisfying a condition — replaces O(n²) nested loops."
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
                "        if   s == 0: res.append([nums[i], nums[l], nums[r]]); l += 1; r -= 1\n"
                "        elif s <  0: l += 1\n"
                "        else:        r -= 1\n"
                "        while l < r and nums[l] == nums[l - 1]: l += 1  # skip dupe\n"
                "        while l < r and r < len(nums) - 1 and nums[r] == nums[r + 1]: r -= 1  # skip dupe"
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
    "pitfalls": (
        "• 3Sum: skip duplicate values at i, l, r to avoid duplicate triplets.\n"
        "• Array must be sorted first — don't forget nums.sort().\n"
        "• Loop condition is left < right (strict), not <=.\n"
        "• Write-pointer: compare nums[i] with nums[i-1] (sorted input), not nums[k-1],\n"
        "  so you always move past all duplicates before deciding to write."
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
