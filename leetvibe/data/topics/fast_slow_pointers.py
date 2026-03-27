from __future__ import annotations

TOPIC: dict = {
    "title": "Fast & Slow Pointers",
    "slug": "Fast Slow Pointers",
    "recognize": (
        "Cycle in linked list, find cycle start, duplicate number, happy number, find middle of list.\n"
        "Signal: detect a cycle or find a midpoint with O(1) space — no hash set."
    ),
    "intuition": (
        "• If a cycle exists, a 2× pointer laps the 1× pointer inside the cycle — they must meet.\n"
        "• After meeting, reset one pointer to head and step both at 1× — they meet exactly at the cycle entry.\n"
        "• This works because the head-to-entry distance equals the meeting-point-to-entry distance (mod cycle length)."
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
    "variants": (
        "• Cycle detection only — phase 1 suffices; return True/False.\n"
        "• Cycle entry node — phase 1 + phase 2 (reset one pointer to head).\n"
        "• Cycle length — after phase 1, keep one fixed and step the other until they meet again; count steps.\n"
        "• Middle of linked list — fast reaches end when slow is at middle; even length lands on second middle.\n"
        "• Find Duplicate Number — encode array as implicit linked list (value = index).\n"
        "• Happy Number — digit-square-sum as next-step function; cycle detection determines if it reaches 1."
    ),
    "pitfalls": (
        "• Phase 2 starts from HEAD (not from meet point) with a fresh pointer.\n"
        "• Middle node: for even-length lists slow lands on the second middle; adjust termination if needed.\n"
        "• Duplicate-number trick requires values in [1, n] — index 0 is the safe starting point."
    ),
    "edge_cases": (
        "• Empty list — fast and fast.next check guards this; return False.\n"
        "• Single node pointing to itself — cycle detected on first iteration.\n"
        "• Cycle at head (F = 0) — phase 2 still works; slow2 starts at head and meets slow immediately.\n"
        "• Even-length list middle — use while fast.next and fast.next.next for first middle instead."
    ),
    "confusion": (
        "┌──────────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with      │ Distinguishing question                             │\n"
        "├──────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Two Pointers             │ Are both pointers on the same list moving toward    │\n"
        "│                          │ each other or maintaining a window? → Two Pointers. │\n"
        "│                          │ Is one pointer moving 2× faster (cycle/middle)?     │\n"
        "│                          │ → Fast & Slow.                                      │\n"
        "├──────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Hash set cycle detection │ O(1) space required? → Fast & Slow (Floyd's).       │\n"
        "│                          │ O(n) space acceptable and simpler code preferred?   │\n"
        "│                          │ → Store visited nodes in a hash set.                │\n"
        "└──────────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Why reset to head in phase 2? Why not keep both at the meeting point?\n"
        "• Can you find the cycle length without extra space?\n"
        "• What if the array in Find Duplicate has multiple duplicates?"
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
