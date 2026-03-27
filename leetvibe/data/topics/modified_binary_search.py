from __future__ import annotations

TOPIC: dict = {
    "title": "Modified Binary Search",
    "slug": "Modified Binary Search",
    "recognize": (
        "Rotated sorted array, find first/last position of target, search in a matrix, find peak element.\n"
        "Signal: sorted array with a twist — rotation, duplicates, 2D layout, or boundary needed."
    ),
    "intuition": (
        "• A rotated array has exactly one breakpoint — at any midpoint, one half is fully sorted.\n"
        "• Check which half is sorted (nums[left] <= nums[mid]), then check if target falls there.\n"
        "• Boundary search: when found, save result and keep shrinking toward the boundary instead of returning."
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
    "patterns": [
        {
            "name": "Search in Rotated Sorted Array",
            "code": (
                "left, right = 0, len(nums) - 1\n"
                "while left <= right:\n"
                "    mid = (left + right) // 2\n"
                "    if nums[mid] == target:\n"
                "        return mid\n"
                "    if nums[left] <= nums[mid]:          # left half is sorted\n"
                "        if nums[left] <= target < nums[mid]:\n"
                "            right = mid - 1\n"
                "        else:\n"
                "            left  = mid + 1\n"
                "    else:                                # right half is sorted\n"
                "        if nums[mid] < target <= nums[right]:\n"
                "            left  = mid + 1\n"
                "        else:\n"
                "            right = mid - 1\n"
                "return -1"
            ),
        },
        {
            "name": "Find First and Last Position (left / right boundary)",
            "code": (
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
        },
    ],
    "variants": (
        "• Rotated sorted array (no duplicates) — sorted-half detection; two range checks per iteration.\n"
        "• Rotated sorted array II (with duplicates) — when nums[left]==nums[mid], fall back to left+=1; O(n) worst case.\n"
        "• Find minimum in rotated array — binary search for breakpoint; if nums[mid] > nums[right], min is right.\n"
        "• First/last position — boundary binary search; record result on match, continue shrinking.\n"
        "• Search in 2D sorted matrix — flatten with mid//cols, mid%cols mapping.\n"
        "• Find peak element — move toward the higher neighbour; guaranteed to converge."
    ),
    "pitfalls": (
        "• Rotated array: determine which half is SORTED first, then check if target falls in that half.\n"
        "• Boundary search: save result when found, keep shrinking — don't return immediately.\n"
        "• Duplicates: when nums[left]==nums[mid], can't determine sorted half — must increment left."
    ),
    "edge_cases": (
        "• Single element — left==right==mid; check and return; no rotation logic fires.\n"
        "• Not rotated (rotation point = 0) — nums[left] ≤ nums[mid] always; degenerates to standard binary search.\n"
        "• Target not in array — result initialised to -1; boundary search returns -1 correctly.\n"
        "• Rotated array with all duplicates — nums[left]==nums[mid]==nums[right]; must increment left; O(n) worst."
    ),
    "confusion": (
        "┌────────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with    │ Distinguishing question                             │\n"
        "├────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Standard Binary Search │ Array sorted without modification? → Standard BS.   │\n"
        "│                        │ Rotation, duplicates, 2D layout? → Modified BS.     │\n"
        "├────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ BS on answer space     │ Searching concrete array values? → Modified BS.     │\n"
        "│                        │ Abstract range with a feasibility function? → BS on │\n"
        "│                        │ answer space.                                       │\n"
        "└────────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What if the rotated array has duplicates — does O(log n) still hold?\n"
        "• Can you find the rotation index in O(log n)?\n"
        "• How would you search in a 2D matrix where rows are sorted but last element of row i may exceed first of row i+1?"
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
