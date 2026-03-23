from __future__ import annotations

TOPIC: dict = {
    "title": "Modified Binary Search",
    "slug": "Modified Binary Search",
    "recognize": (
        "rotated sorted array, find first/last position of target,\n"
        "  search in a matrix, \"find peak element\", bitonic array."
    ),
    "diagram": (
        "  Rotated sorted array — which half is sorted?\n"
        "  idx:  0    1    2    3    4    5    6\n"
        "  arr:  4    5    6    7    0    1    2    target = 0\n"
        "             L              M              R\n"
        "\n"
        "  arr[L] <= arr[M]  →  LEFT half is sorted  (4..7)\n"
        "  target NOT in [4, 7]  →  search RIGHT half\n"
        "\n"
        "  Find first/last position — shrink toward boundary:\n"
        "  [5  7  7  8  8  10]   target=8\n"
        "  first: when found, set right=mid-1 to keep shrinking left\n"
        "  last:  when found, set left=mid+1  to keep shrinking right"
    ),
    "when": (
        "Sorted array with a twist: rotation, duplicates, a 2D matrix,\n"
        "  or any search space where the standard pivot logic breaks."
    ),
    "pattern": (
        "# Search in Rotated Sorted Array\n"
        "left, right = 0, len(nums) - 1\n"
        "while left <= right:\n"
        "    mid = (left + right) // 2\n"
        "    if nums[mid] == target:\n"
        "        return mid\n"
        "    if nums[left] <= nums[mid]:          # left half is sorted\n"
        "        if nums[left] <= target < nums[mid]:\n"
        "            right = mid - 1              # target in left half\n"
        "        else:\n"
        "            left  = mid + 1              # target in right half\n"
        "    else:                                # right half is sorted\n"
        "        if nums[mid] < target <= nums[right]:\n"
        "            left  = mid + 1\n"
        "        else:\n"
        "            right = mid - 1\n"
        "return -1"
    ),
    "pattern2": (
        "# Find First and Last Position (left / right boundary)\n"
        "def binary_boundary(nums, target, find_left):\n"
        "    left, right, result = 0, len(nums) - 1, -1\n"
        "    while left <= right:\n"
        "        mid = (left + right) // 2\n"
        "        if nums[mid] == target:\n"
        "            result = mid\n"
        "            if find_left: right = mid - 1  # keep going left\n"
        "            else:         left  = mid + 1  # keep going right\n"
        "        elif nums[mid] < target:\n"
        "            left  = mid + 1\n"
        "        else:\n"
        "            right = mid - 1\n"
        "    return result\n"
        "\n"
        "# Search a 2D Matrix (treat as flat sorted array)\n"
        "rows, cols = len(matrix), len(matrix[0])\n"
        "left, right = 0, rows * cols - 1\n"
        "while left <= right:\n"
        "    mid = (left + right) // 2\n"
        "    val = matrix[mid // cols][mid % cols]\n"
        "    if   val == target: return True\n"
        "    elif val  < target: left  = mid + 1\n"
        "    else:               right = mid - 1\n"
        "return False"
    ),
    "pitfalls": (
        "• Rotated array: check which HALF is sorted first, then check if\n"
        "  target falls within that half — don't compare to mid blindly.\n"
        "• Boundary search: save result when found, then keep shrinking\n"
        "  (don't return immediately) to find the true boundary.\n"
        "• Find Peak Element: valid to go toward the higher neighbour;\n"
        "  always converges because peaks must exist at boundaries."
    ),
    "time": "O(log n)",
    "space": "O(1)",
    "problems": [
        ("Search in Rotated Sorted Array",           "M"),
        ("Find Minimum in Rotated Sorted Array",     "M"),
        ("Find First and Last Position of Element",  "M"),
        ("Search a 2D Matrix",                       "M"),
        ("Find Peak Element",                        "M"),
        ("Search in Rotated Sorted Array II",        "M"),
    ],
    "related": ["Binary Search", "Two Pointers", "Fast & Slow Pointers"],
}
