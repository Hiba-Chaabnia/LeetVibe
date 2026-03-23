from __future__ import annotations

TOPIC: dict = {
    "title": "Sorting Algorithms",
    "slug": "Sorting",
    "recognize": (
        "\"sort the array\", choosing the right sort for the constraint:\n"
        "  nearly sorted → insertion, many duplicates → 3-way partition,\n"
        "  stable required → merge/Timsort, O(n) possible → counting/radix."
    ),
    "diagram": (
        "  Algorithm      Time (avg)   Time (worst)  Space  Stable?\n"
        "  ─────────────────────────────────────────────────────────\n"
        "  Bubble Sort    O(n²)        O(n²)         O(1)   ✓\n"
        "  Insertion Sort O(n²)        O(n²)         O(1)   ✓  ← best for tiny/nearly-sorted\n"
        "  Merge Sort     O(n log n)   O(n log n)    O(n)   ✓  ← Python's sorted() / .sort()\n"
        "  Heap Sort      O(n log n)   O(n log n)    O(1)   ✗\n"
        "  Quick Sort     O(n log n)   O(n²)         O(log n) ✗  ← fast in practice\n"
        "  Counting Sort  O(n + k)     O(n + k)      O(k)   ✓  ← k = value range\n"
        "  Radix Sort     O(n · d)     O(n · d)      O(n+k) ✓  ← d = number of digits\n"
        "\n"
        "  Python's sort is Timsort (hybrid merge + insertion), stable, O(n log n)."
    ),
    "when": (
        "Most interview problems just call sorted() or .sort().\n"
        "  Know the templates when asked to implement, or when a linear-time\n"
        "  sort is possible (small integer range → counting/radix)."
    ),
    "pattern": (
        "# Python built-ins — always prefer these in interviews\n"
        "arr.sort()                           # in-place, stable, O(n log n)\n"
        "arr.sort(key=lambda x: x[1])         # sort by second element\n"
        "arr.sort(key=lambda x: (-x[0], x[1]))# descending primary, ascending secondary\n"
        "sorted(arr, reverse=True)            # returns new list\n"
        "\n"
        "# Quick Sort — O(n log n) avg, O(1) extra space\n"
        "def quicksort(arr, lo, hi):\n"
        "    if lo >= hi: return\n"
        "    pivot = arr[hi]\n"
        "    i = lo\n"
        "    for j in range(lo, hi):\n"
        "        if arr[j] <= pivot:\n"
        "            arr[i], arr[j] = arr[j], arr[i]\n"
        "            i += 1\n"
        "    arr[i], arr[hi] = arr[hi], arr[i]   # place pivot\n"
        "    quicksort(arr, lo, i - 1)\n"
        "    quicksort(arr, i + 1, hi)\n"
        "\n"
        "# Counting Sort — O(n + k) for integers in [0, k)\n"
        "def counting_sort(arr, k):\n"
        "    count = [0] * k\n"
        "    for x in arr: count[x] += 1\n"
        "    result = []\n"
        "    for val, freq in enumerate(count):\n"
        "        result.extend([val] * freq)\n"
        "    return result"
    ),
    "pattern2": (
        "# Merge Sort — O(n log n), stable, O(n) extra space\n"
        "def mergesort(arr):\n"
        "    if len(arr) <= 1: return arr\n"
        "    mid   = len(arr) // 2\n"
        "    left  = mergesort(arr[:mid])\n"
        "    right = mergesort(arr[mid:])\n"
        "    return merge(left, right)\n"
        "\n"
        "def merge(l, r):\n"
        "    result = []\n"
        "    i = j = 0\n"
        "    while i < len(l) and j < len(r):\n"
        "        if l[i] <= r[j]: result.append(l[i]); i += 1\n"
        "        else:            result.append(r[j]); j += 1\n"
        "    return result + l[i:] + r[j:]\n"
        "\n"
        "# 3-way Partition (Dutch National Flag) — O(n), handles many duplicates\n"
        "# Partition arr into: < pivot | == pivot | > pivot\n"
        "def three_way_partition(arr, pivot):\n"
        "    lo, mid, hi = 0, 0, len(arr) - 1\n"
        "    while mid <= hi:\n"
        "        if   arr[mid] < pivot: arr[lo], arr[mid] = arr[mid], arr[lo]; lo += 1; mid += 1\n"
        "        elif arr[mid] > pivot: arr[mid], arr[hi] = arr[hi], arr[mid]; hi -= 1\n"
        "        else:                  mid += 1\n"
        "    return arr\n"
        "# Also solves: Sort Colors (LeetCode 75)"
    ),
    "pitfalls": (
        "• Python's .sort() / sorted() are stable Timsort — always use them unless\n"
        "  you're explicitly asked to implement a sorting algorithm.\n"
        "• Quick Sort worst case O(n²) on already-sorted input with last-element pivot;\n"
        "  randomise the pivot or use median-of-3 to avoid it.\n"
        "• Counting Sort: only works for non-negative integers with bounded range k;\n"
        "  for strings or floats, use radix sort or comparison sort.\n"
        "• sort(key=...) uses a single key; for multi-key sorts, use a tuple key\n"
        "  or functools.cmp_to_key() for custom comparators."
    ),
    "time": "O(n log n) comparison sorts  /  O(n + k) counting  /  O(n·d) radix",
    "space": "O(n) merge sort  /  O(log n) quicksort stack  /  O(k) counting",
    "problems": [
        ("Sort Colors",                    "M"),
        ("Largest Number",                 "M"),
        ("Sort Array by Parity",           "E"),
        ("Wiggle Sort II",                 "M"),
        ("Maximum Gap",                    "H"),
        ("Sort Characters by Frequency",   "M"),
    ],
    "related": ["Arrays & Hashing", "Two Pointers", "Merge Sort / Divide & Conquer"],
}
