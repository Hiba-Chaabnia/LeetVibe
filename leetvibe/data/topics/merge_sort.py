from __future__ import annotations

TOPIC: dict = {
    "title": "Merge Sort / Divide & Conquer",
    "slug": "Merge Sort",
    "recognize": (
        "\"sort a linked list\", \"count inversions\", \"K-th element via partition\",\n"
        "  \"merge K sorted lists\", divide problem in half recursively."
    ),
    "diagram": (
        "  Merge Sort — split, recurse, merge:\n"
        "  [5, 2, 4, 1, 3]\n"
        "      ↙          ↘\n"
        "  [5, 2]      [4, 1, 3]\n"
        "   ↙  ↘        ↙     ↘\n"
        "  [5]  [2]   [4]   [1, 3]\n"
        "   ↘  ↙       ↘   ↙\n"
        "  [2, 5]     [1, 3, 4]\n"
        "       ↘    ↙\n"
        "   [1, 2, 3, 4, 5]   ← merged\n"
        "\n"
        "  O(n log n) time   O(n) space (merge buffer)"
    ),
    "when": (
        "Sorting a linked list (no random access → can't use quicksort).\n"
        "  Counting inversions. Any divide-and-conquer where merging\n"
        "  two sorted halves produces useful information."
    ),
    "pattern": (
        "# Merge Sort on a Linked List (Sort List)\n"
        "def sort_list(head):\n"
        "    if not head or not head.next: return head\n"
        "\n"
        "    # Find middle using slow/fast pointers\n"
        "    slow, fast = head, head.next\n"
        "    while fast and fast.next:\n"
        "        slow, fast = slow.next, fast.next.next\n"
        "    mid        = slow.next\n"
        "    slow.next  = None          # split the list\n"
        "\n"
        "    left  = sort_list(head)\n"
        "    right = sort_list(mid)\n"
        "    return merge(left, right)\n"
        "\n"
        "def merge(l1, l2):\n"
        "    dummy = ListNode(0)\n"
        "    curr  = dummy\n"
        "    while l1 and l2:\n"
        "        if l1.val <= l2.val: curr.next = l1; l1 = l1.next\n"
        "        else:                curr.next = l2; l2 = l2.next\n"
        "        curr = curr.next\n"
        "    curr.next = l1 or l2\n"
        "    return dummy.next"
    ),
    "pattern2": (
        "# Count Inversions — augment merge sort to count during merge\n"
        "def merge_count(arr):\n"
        "    if len(arr) <= 1: return arr, 0\n"
        "    mid = len(arr) // 2\n"
        "    left,  lc = merge_count(arr[:mid])\n"
        "    right, rc = merge_count(arr[mid:])\n"
        "    merged, mc = [], 0\n"
        "    i = j = 0\n"
        "    while i < len(left) and j < len(right):\n"
        "        if left[i] <= right[j]:\n"
        "            merged.append(left[i]); i += 1\n"
        "        else:\n"
        "            merged.append(right[j]); j += 1\n"
        "            mc += len(left) - i    # all remaining left elements > right[j]\n"
        "    merged += left[i:] + right[j:]\n"
        "    return merged, lc + rc + mc\n"
        "\n"
        "# Quick Select — K-th largest in O(n) average\n"
        "import random\n"
        "def quick_select(nums, k):\n"
        "    pivot = random.choice(nums)\n"
        "    lo = [x for x in nums if x < pivot]\n"
        "    eq = [x for x in nums if x == pivot]\n"
        "    hi = [x for x in nums if x > pivot]\n"
        "    if   k <= len(hi):             return quick_select(hi, k)\n"
        "    elif k <= len(hi) + len(eq):   return pivot\n"
        "    else:                          return quick_select(lo, k - len(hi) - len(eq))"
    ),
    "pitfalls": (
        "• Linked list merge sort: split by finding middle WITH slow.next = None\n"
        "  to disconnect the two halves — forgetting this causes infinite recursion.\n"
        "• Count inversions: the count is len(left) - i, NOT just 1, when right[j]\n"
        "  is smaller — all remaining left elements are also greater.\n"
        "• Quick Select: worst case O(n²) with bad pivot; randomise to avoid it.\n"
        "• Arrays merge sort needs O(n) extra space; linked list version is O(log n)."
    ),
    "time": "O(n log n) merge sort   /   O(n) avg Quick Select",
    "space": "O(n) merge sort arrays   /   O(log n) linked list (recursion stack)",
    "problems": [
        ("Sort List", "M"),
        ("Merge K Sorted Lists", "H"),
        ("Kth Largest Element in an Array", "M"),
        ("Count of Smaller Numbers After Self", "H"),
        ("Find Median from Two Sorted Arrays", "H"),
        ("Reverse Pairs", "H"),
    ],
    "related": ["Linked List", "Fast & Slow Pointers", "Heap / Priority Queue"],
}
