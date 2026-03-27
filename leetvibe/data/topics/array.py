from __future__ import annotations

TOPIC: dict = {
    "title": "Arrays & Hashing",
    "slug": "Array",
    "recognize": (
        "Duplicate, count frequency, group by, two elements satisfying a sum condition, anagram detection.\n"
        "Keywords: fast O(1) lookup, counting frequencies, detecting duplicates, grouping by a computed key."
    ),
    "intuition": (
        "• Hash map stores value→index in O(1), so complement lookup drops O(n²) to O(n).\n"
        "• Kadane's: the max subarray ending at i is either nums[i] alone (restart) or extended from i-1.\n"
        "• Once cur goes negative, starting fresh is always better — no previous prefix can help."
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
    "patterns": [
        {
            "name": "Two Sum — look up complement in hash map",
            "code": (
                "seen = {}\n"
                "for i, val in enumerate(arr):\n"
                "    complement = target - val\n"
                "    if complement in seen:\n"
                "        return [seen[complement], i]\n"
                "    seen[val] = i"
            ),
        },
        {
            "name": "Group Anagrams — hash by sorted key",
            "code": (
                "from collections import defaultdict\n"
                "groups = defaultdict(list)\n"
                "for word in words:\n"
                "    key = tuple(sorted(word))   # or tuple(Counter(word).items())\n"
                "    groups[key].append(word)\n"
                "return list(groups.values())\n"
                "\n"
                "# Kadane's Algorithm — Maximum Subarray  O(n) time  O(1) space\n"
                "max_sum = cur = nums[0]\n"
                "for num in nums[1:]:\n"
                "    cur     = max(num, cur + num)   # restart if cur went negative\n"
                "    max_sum = max(max_sum, cur)\n"
                "return max_sum\n"
                "\n"
                "# Maximum Sum Circular Subarray\n"
                "# Case 1: normal Kadane (subarray does not wrap)\n"
                "# Case 2: total_sum - min_subarray (subarray wraps)\n"
                "total = sum(nums)\n"
                "max_sum = cur_max = nums[0]\n"
                "min_sum = cur_min = nums[0]\n"
                "for num in nums[1:]:\n"
                "    cur_max = max(num, cur_max + num)\n"
                "    max_sum = max(max_sum, cur_max)\n"
                "    cur_min = min(num, cur_min + num)\n"
                "    min_sum = min(min_sum, cur_min)\n"
                "# all-negative edge case: min_sum==total → return plain max_sum\n"
                "return max(max_sum, total - min_sum) if max_sum > 0 else max_sum"
            ),
        },
    ],
    "variants": (
        "• Two Sum (single pair) — hash map; store value→index.\n"
        "• Two Sum II (sorted) — two pointers instead; O(1) space.\n"
        "• k-Sum — fix k-2 elements with loops, reduce inner two to Two Sum.\n"
        "• Group Anagrams by sorted key — tuple(sorted(word)) as dict key.\n"
        "• Group Anagrams by frequency key — tuple of 26 char counts; avoids sorting.\n"
        "• Maximum Subarray (Kadane's) — track cur and max_sum; restart on negative.\n"
        "• Maximum Sum Circular Subarray — Kadane's + (total − min_subarray); guard all-negative.\n"
        "• Longest Consecutive Sequence — set; only start chain when num-1 is absent."
    ),
    "pitfalls": (
        "• Use defaultdict if missing keys matter; plain dict raises KeyError.\n"
        "• Counter counts duplicates — it is NOT a set.\n"
        "• tuple(sorted()) as dict key; list is unhashable.\n"
        "• Kadane's: initialise max_sum = nums[0], not 0 — handles all-negative input."
    ),
    "edge_cases": (
        "• Empty array — Kadane's crashes on nums[0] (Two Sum just returns nothing); guard with 'if not nums'.\n"
        "• All negative numbers — Kadane's initialised to nums[0] handles this; 0 initialisation silently returns 0.\n"
        "• Circular subarray where all elements are negative — total − min_sum = 0; return plain max_sum.\n"
        "• Duplicate index in Two Sum — store seen[val] = i AFTER checking, not before."
    ),
    "confusion": (
        "┌─────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                             │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Sliding Window      │ Do you need a contiguous subarray with a size/sum   │\n"
        "│                     │ constraint? → Sliding Window.                       │\n"
        "│                     │ Do you need to look up or group arbitrary elements? │\n"
        "│                     │ → Arrays & Hashing.                                 │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Two Pointers        │ Is the array sorted (or can it be sorted cheaply)?  │\n"
        "│                     │ → Two Pointers (O(1) space).                        │\n"
        "│                     │ Must you preserve original indices? → Hash Map.     │\n"
        "└─────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Two Sum: What if there can be multiple valid pairs — return all of them?\n"
        "• Two Sum: What if the array is sorted? Can you do it in O(1) space?\n"
        "• Kadane's: What if the array can wrap around (circular)?\n"
        "• Group Anagrams: Can you avoid sorting each word?"
    ),
    "time": "O(n)",
    "space": "O(n)",
    "problems": [
        ("Two Sum",                           "E"),
        ("Contains Duplicate",                "E"),
        ("Valid Anagram",                     "E"),
        ("Maximum Subarray",                  "M"),
        ("Maximum Sum Circular Subarray",     "M"),
        ("Group Anagrams",                    "M"),
        ("Longest Consecutive Sequence",      "M"),
    ],
    "related": ["Sliding Window", "Two Pointers", "Cyclic Sort"],
}
