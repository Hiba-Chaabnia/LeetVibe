from __future__ import annotations

TOPIC: dict = {
    "title": "Linked List",
    "slug": "Linked List",
    "recognize": (
        "Reversal, cycle detection, find middle, merge sorted lists, remove N-th from end, reorder list.\n"
        "Signal: pointer manipulation — no index arithmetic, use a dummy head."
    ),
    "intuition": (
        "• Use a dummy head node — it gives every node a 'previous', eliminating edge cases for empty list and head deletion.\n"
        "• Iterative reversal: prev/curr swap in 3 lines; after the loop, prev is the new head.\n"
        "• Gap trick for N-th from end: advance right n steps, then move both until right is None."
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
    "patterns": [
        {
            "name": "Reverse a linked list",
            "code": (
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
        },
        {
            "name": "Remove Nth node from end — one pass with gap",
            "code": (
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
                "# Reverse Nodes in k-Group\n"
                "def get_kth(curr, k):\n"
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
                "    tmp = group_prev.next\n"
                "    group_prev.next = kth\n"
                "    group_prev = tmp\n"
                "return dummy.next"
            ),
        },
    ],
    "variants": (
        "• Reverse entire list — iterative prev/curr swap; O(n), O(1).\n"
        "• Reverse sublist [left, right] — advance to node before sublist; front-insertion trick.\n"
        "• Reverse in k-groups — get_kth check; reverse each group; leave remainder as-is.\n"
        "• Find middle — even length: slow lands on second middle; use fast.next and fast.next.next for first.\n"
        "• Remove N-th from end — gap technique with dummy head; one pass.\n"
        "• Merge two sorted lists — compare heads; advance the smaller; O(n+m).\n"
        "• Reorder list — find middle, reverse second half, merge alternately.\n"
        "• Copy list with random pointer — two-pass hash map, or interleave clones in-place for O(1) space."
    ),
    "pitfalls": (
        "• Use a dummy head — it eliminates empty-list and head-deletion edge cases.\n"
        "• Cycle start (phase 2): reset one pointer to HEAD, step both at 1×; they meet at the cycle entry.\n"
        "• Reverse in groups: save group_prev.next before reversing — it becomes the tail and the next group_prev.\n"
        "• Partial reverse (Reverse II): the front-insertion trick inserts one node at a time — draw it out first."
    ),
    "edge_cases": (
        "• Empty list — dummy head guards this; return dummy.next = None.\n"
        "• Remove head (n = list length) — left stays at dummy; left.next = left.next.next skips head.\n"
        "• k-Group where n is not a multiple of k — get_kth returns None; remainder left as-is.\n"
        "• Single node — reverse returns it unchanged; all other ops handle correctly."
    ),
    "confusion": (
        "┌───────────────────────┬────────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                            │\n"
        "├───────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Two Pointers (arrays) │ Is it a linked list with next pointers? → DLL/SLL  │\n"
        "│                       │ techniques (dummy head, gap trick). Array indices? │\n"
        "│                       │ → Two Pointers.                                    │\n"
        "├───────────────────────┼────────────────────────────────────────────────────┤\n"
        "│ Fast & Slow Pointers  │ Cycle detection or finding middle? → Fast & Slow.  │\n"
        "│                       │ Reversal, removal, or merging? → Linked List.      │\n"
        "└───────────────────────┴────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you reverse a linked list recursively? What's the space cost?\n"
        "• How would you detect if a linked list is a palindrome in O(n) time and O(1) space?\n"
        "• Your k-group reversal leaves the last partial group unreversed — what if the problem requires reversing it?"
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
