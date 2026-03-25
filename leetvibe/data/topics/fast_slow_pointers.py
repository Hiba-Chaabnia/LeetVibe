from __future__ import annotations

TOPIC: dict = {
    "title": "Fast & Slow Pointers",
    "slug": "Fast Slow Pointers",
    "recognize": (
        "cycle in linked list, find cycle start, duplicate number,\n"
        "happy number, find middle of list without extra space."
    ),
    "diagram": (
        "  Floyd's cycle detection:\n"
        "\n"
        "  Phase 1 — detect cycle:\n"
        "  slow +1, fast +2 each step:\n"
        "  [1]→[2]→[3]→[4]→[5]\n"
        "                ↑____↑  ← cycle\n"
        "  They meet somewhere inside the cycle.\n"
        "\n"
        "  Phase 2 — find cycle start:\n"
        "  Reset one pointer to head, keep other at meet point.\n"
        "  Move both +1 each step → they meet at cycle entry."
    ),
    "when": (
        "Cycle detection in a linked list or implicit sequence.\n"
        "Finding the middle of a list. Detecting duplicate values\n"
        "when the array encodes a function (value = next index)."
    ),
    "patterns": [
        {
            "name": "Detect cycle (phase 1)",
            "code": (
                "slow = fast = head\n"
                "has_cycle = False\n"
                "while fast and fast.next:\n"
                "    slow, fast = slow.next, fast.next.next\n"
                "    if slow is fast:\n"
                "        has_cycle = True\n"
                "        break\n"
                "\n"
                "# Find cycle START (phase 2)\n"
                "if has_cycle:\n"
                "    slow2 = head\n"
                "    while slow2 is not slow:\n"
                "        slow2 = slow2.next\n"
                "        slow  = slow.next\n"
                "    # slow2 is now the cycle entry node"
            ),
        },
        {
            "name": "Find Duplicate Number — array as implicit linked list",
            "code": (
                "# nums contains n+1 integers in [1, n]; treat value as next index.\n"
                "slow = fast = nums[0]\n"
                "while True:                        # phase 1: find meeting point\n"
                "    slow = nums[slow]\n"
                "    fast = nums[nums[fast]]\n"
                "    if slow == fast: break\n"
                "\n"
                "slow2 = nums[0]                    # phase 2: find entry (duplicate)\n"
                "while slow != slow2:\n"
                "    slow  = nums[slow]\n"
                "    slow2 = nums[slow2]\n"
                "return slow\n"
                "\n"
                "# Middle of Linked List\n"
                "slow = fast = head\n"
                "while fast and fast.next:\n"
                "    slow, fast = slow.next, fast.next.next\n"
                "return slow    # for even length, slow is the SECOND middle"
            ),
        },
    ],
    "pitfalls": (
        "• Phase 2 starts from HEAD (not from meet point) with a fresh pointer.\n"
        "• Middle node: for even-length lists slow lands on the second middle;\n"
        "  adjust the termination condition if you need the first middle.\n"
        "• The duplicate-number trick requires values in [1, n] — index 0 is safe\n"
        "  as a starting point because it is never a valid next-step target."
    ),
    "time": "O(n)",
    "space": "O(1)",
    "problems": [
        ("Linked List Cycle",         "E"),
        ("Linked List Cycle II",      "M"),
        ("Middle of the Linked List", "E"),
        ("Find the Duplicate Number", "M"),
        ("Happy Number",              "E"),
        ("Palindrome Linked List",    "E"),
    ],
    "related": ["Linked List", "Two Pointers", "Cyclic Sort"],
}
