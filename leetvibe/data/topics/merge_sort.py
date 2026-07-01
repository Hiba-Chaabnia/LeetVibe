from __future__ import annotations

TOPIC: dict = {
    "title": "Merge Sort / Divide & Conquer",
    "slug": "Merge Sort",
    "recognize": (
        "Sort a linked list, count inversions, K-th element via partition, merge K sorted lists.\n"
        "Signal: 'sort without random access', or 'count cross-partition relationships during merge'."
    ),
    "intuition": (
        "• Split in half recursively (log n levels); merge in O(n) per level — total O(n log n).\n"
        "• During merge, when right[j] < left[i], ALL remaining left elements form inversions with right[j] — count len(left)-i.\n"
        "• Linked list: use slow/fast pointer to find middle; no random access needed, unlike quicksort."
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
    "patterns": [
        {
            "name": "Merge Sort on a Linked List (Sort List)",
            "code": (
                "def sort_list(head):\n"
                "    if not head or not head.next: return head\n"
                "\n"
                "    slow, fast = head, head.next\n"
                "    while fast and fast.next:\n"
                "        slow, fast = slow.next, fast.next.next\n"
                "    mid        = slow.next\n"
                "    slow.next  = None          # split\n"
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
        },
        {
            "name": "Count Inversions + Quick Select",
            "code": (
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
                "            mc += len(left) - i    # all remaining left > right[j]\n"
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
        },
    ],
    "variants": (
        "• Merge sort on arrays — O(n log n) time, O(n) auxiliary space for merge buffer.\n"
        "• Merge sort on linked list — O(n log n) time, O(log n) space (recursion stack, no buffer).\n"
        "• Count inversions — augment merge: when right[j] < left[i], add len(left)-i.\n"
        "• Quick Select (K-th largest) — partition; recurse one side; O(n) average, O(n²) worst; randomise pivot.\n"
        "• Merge K sorted lists — min-heap of (val, list_idx, node); O(n log k).\n"
        "• Augmented divide-and-conquer — Count of Smaller Numbers, Reverse Pairs."
    ),
    "pitfalls": (
        "• Linked list split: set slow.next = None to disconnect the two halves — forgetting causes infinite recursion.\n"
        "• Count inversions: increment is len(left) - i, NOT 1 — all remaining left elements are also inversions.\n"
        "• Quick Select: worst case O(n²) with bad pivot — randomise to avoid adversarial inputs.\n"
        "• Arrays merge sort needs O(n) extra space; linked list version is O(log n)."
    ),
    "edge_cases": (
        "• Empty list or single element — base case returns immediately; no split.\n"
        "• All identical elements — merge always takes from left (≤); inversion count = 0.\n"
        "• Already sorted input — merge sort is still O(n log n); Python's Timsort detects runs and runs O(n).\n"
        "• Linked list even length — slow/fast with fast=head.next gives equal halves; verify the split point."
    ),
    "confusion": (
        "┌─────────────────────┬────────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                                │\n"
        "├─────────────────────┼────────────────────────────────────────────────────────┤\n"
        "│ Heap (Top-K)        │ K-th largest once from unsorted? → Quick Select O(n).  │\n"
        "│                     │ Top-K repeatedly from a stream? → Min-heap O(n log k). │\n"
        "├─────────────────────┼────────────────────────────────────────────────────────┤\n"
        "│ Quicksort           │ In-place O(1) extra space, O(n log n) average?         │\n"
        "│                     │ → Quicksort.                                           │\n"
        "│                     │ Guaranteed O(n log n) worst case, or sorting           │\n"
        "│                     │ a linked list? → Merge Sort.                           │\n"
        "└─────────────────────┴────────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why can't you use quicksort on a linked list?\n"
        "• Can you count inversions in O(n log n) without copying subarrays?\n"
        "• Quick Select is O(n) average but O(n²) worst — is there an O(n) worst-case algorithm?"
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
