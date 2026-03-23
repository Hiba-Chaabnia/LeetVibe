from __future__ import annotations

TOPIC: dict = {
    "title": "Arrays & Hashing",
    "slug": "Array",
    "recognize": (
        "\"duplicate\", \"count frequency\", \"group by\", \"two elements\"\n"
        "  satisfying a sum condition, anagram detection.\n"
        "  set() for O(1) membership, Counter for frequency maps."
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
    "when": (
        "Fast O(1) lookups, counting frequencies, detecting duplicates,\n"
        "  or grouping elements by a computed key."
    ),
    "pattern": (
        "# Two Sum — look up complement in hash map\n"
        "seen = {}\n"
        "for i, val in enumerate(arr):\n"
        "    complement = target - val\n"
        "    if complement in seen:\n"
        "        return [seen[complement], i]\n"
        "    seen[val] = i"
    ),
    "pattern2": (
        "# Group Anagrams — hash by sorted key\n"
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
    "pitfalls": (
        "• defaultdict vs plain dict — plain dict raises KeyError on missing key.\n"
        "• Counter is not a set; it counts duplicates, not deduplicates.\n"
        "• tuple(sorted()) works as a dict key; list is unhashable.\n"
        "• Kadane's: must initialise max_sum = nums[0], not 0 (handles all-negative)."
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
