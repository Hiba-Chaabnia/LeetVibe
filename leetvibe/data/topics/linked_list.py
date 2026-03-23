from __future__ import annotations

TOPIC: dict = {
    "title": "Linked List",
    "slug": "Linked List",
    "recognize": (
        "reversal, cycle detection, find middle, merge sorted lists,\n"
        "  remove N-th from end, reorder list."
    ),
    "diagram": (
        "  head\n"
        "   ↓\n"
        "  [1] → [2] → [3] → [4] → None\n"
        "\n"
        "  fast / slow pointers (Floyd's cycle detection):\n"
        "   s         f\n"
        "  [1] → [2] → [3] → [4] → [5]\n"
        "                ↑____________↑\n"
        "   slow +1, fast +2 → meet inside cycle → cycle exists"
    ),
    "when": (
        "Reversals, cycle detection, finding the middle,\n"
        "  merging sorted lists, or removing the N-th node."
    ),
    "pattern": (
        "# Reverse a linked list\n"
        "prev, curr = None, head\n"
        "while curr:\n"
        "    nxt        = curr.next\n"
        "    curr.next  = prev\n"
        "    prev, curr = curr, nxt\n"
        "return prev\n"
        "\n"
        "# Find middle (slow/fast)\n"
        "slow = fast = head\n"
        "while fast and fast.next:\n"
        "    slow, fast = slow.next, fast.next.next\n"
        "# slow is now at the middle"
    ),
    "pattern2": (
        "# Remove Nth node from end — one pass with gap\n"
        "dummy = ListNode(0, head)\n"
        "left, right = dummy, head\n"
        "for _ in range(n):         # advance right by n steps\n"
        "    right = right.next\n"
        "while right:               # move both until right hits end\n"
        "    left, right = left.next, right.next\n"
        "left.next = left.next.next # delete target\n"
        "return dummy.next\n"
        "\n"
        "# Reverse Linked List II — reverse nodes from pos left to right\n"
        "dummy = ListNode(0, head)\n"
        "prev = dummy\n"
        "for _ in range(left - 1):          # advance to node before sublist\n"
        "    prev = prev.next\n"
        "curr = prev.next\n"
        "for _ in range(right - left):      # reverse right-left times\n"
        "    nxt        = curr.next\n"
        "    curr.next  = nxt.next\n"
        "    nxt.next   = prev.next\n"
        "    prev.next  = nxt\n"
        "return dummy.next\n"
        "\n"
        "# Reverse Nodes in k-Group — reverse each chunk of k\n"
        "def get_kth(curr, k):              # check if k nodes remain\n"
        "    while curr and k > 0:\n"
        "        curr = curr.next; k -= 1\n"
        "    return curr\n"
        "\n"
        "dummy = ListNode(0, head)\n"
        "group_prev = dummy\n"
        "while True:\n"
        "    kth = get_kth(group_prev, k)\n"
        "    if not kth: break\n"
        "    group_next = kth.next\n"
        "    prev, curr = kth.next, group_prev.next\n"
        "    while curr != group_next:\n"
        "        nxt = curr.next\n"
        "        curr.next = prev\n"
        "        prev = curr; curr = nxt\n"
        "    tmp = group_prev.next       # connect reversed group back\n"
        "    group_prev.next = kth\n"
        "    group_prev = tmp\n"
        "return dummy.next"
    ),
    "pitfalls": (
        "• Use a dummy head node to simplify edge cases (empty list, head deletion).\n"
        "• Cycle start: after slow/fast meet, reset one pointer to head, step both by 1.\n"
        "• Reverse in groups: save group_prev.next before reversing — it becomes\n"
        "  the tail of the reversed group and the new group_prev for the next chunk.\n"
        "• Reverse II (partial): the insertion trick (nxt.next = prev.next, prev.next = nxt)\n"
        "  inserts nodes one-by-one at the front of the sublist — draw it out first."
    ),
    "time": "O(n)",
    "space": "O(1)",
    "problems": [
        ("Reverse Linked List",                  "E"),
        ("Merge Two Sorted Lists",               "E"),
        ("Linked List Cycle",                    "E"),
        ("Remove Nth Node From End",             "M"),
        ("Reorder List",                         "M"),
        ("Copy List with Random Pointer",        "M"),
    ],
    "related": ["Two Pointers", "Stack", "Fast & Slow Pointers"],
}
