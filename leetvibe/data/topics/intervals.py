from __future__ import annotations

TOPIC: dict = {
    "title": "Intervals",
    "slug": "Intervals",
    "recognize": (
        "Overlapping, scheduling, meeting rooms, insert interval, merge ranges, minimum removals.\n"
        "Signal: [start, end] pairs where overlaps must be detected, merged, or counted."
    ),
    "intuition": (
        "• Sorting by start time means overlaps can only occur between consecutive intervals — one pass suffices.\n"
        "• Merge condition: next.start ≤ current.end; extend current.end to max(current.end, next.end).\n"
        "• Meeting rooms: a min-heap of end times lets you reuse the earliest-finishing room in O(log n)."
    ),
    "diagram": (
        "  Merge overlapping intervals:\n"
        "  input:   [1──3]  [2────5]  [6──8]  [9─10]\n"
        "  sort by start, merge if next.start <= current.end:\n"
        "  output:  [1────────5]      [6──8]  [9─10]\n"
        "\n"
        "  overlap condition:  next.start  <=  current.end"
    ),
    "patterns": [
        {
            "name": "Merge intervals",
            "code": (
                "intervals.sort(key=lambda x: x[0])\n"
                "merged = [intervals[0]]\n"
                "for start, end in intervals[1:]:\n"
                "    if start <= merged[-1][1]:           # overlapping\n"
                "        merged[-1][1] = max(merged[-1][1], end)\n"
                "    else:\n"
                "        merged.append([start, end])\n"
                "return merged"
            ),
        },
        {
            "name": "Insert Interval — 3-phase: before / overlap / after",
            "code": (
                "result = []\n"
                "i, n = 0, len(intervals)\n"
                "\n"
                "# Phase 1: add all intervals that end before new_interval starts\n"
                "while i < n and intervals[i][1] < new_interval[0]:\n"
                "    result.append(intervals[i]); i += 1\n"
                "\n"
                "# Phase 2: merge all overlapping intervals into new_interval\n"
                "while i < n and intervals[i][0] <= new_interval[1]:\n"
                "    new_interval[0] = min(new_interval[0], intervals[i][0])\n"
                "    new_interval[1] = max(new_interval[1], intervals[i][1])\n"
                "    i += 1\n"
                "result.append(new_interval)\n"
                "\n"
                "# Phase 3: add all intervals that start after new_interval ends\n"
                "while i < n:\n"
                "    result.append(intervals[i]); i += 1\n"
                "return result\n"
                "\n"
                "# Meeting Rooms II — minimum rooms (min-heap of end times)\n"
                "import heapq\n"
                "intervals.sort(key=lambda x: x[0])\n"
                "heap = []   # end times of ongoing meetings\n"
                "for start, end in intervals:\n"
                "    if heap and heap[0] <= start:\n"
                "        heapq.heapreplace(heap, end)  # reuse a room\n"
                "    else:\n"
                "        heapq.heappush(heap, end)     # new room needed\n"
                "return len(heap)"
            ),
        },
    ],
    "variants": (
        "• Merge overlapping intervals — sort by start; extend running end; O(n log n).\n"
        "• Insert interval into sorted list — 3-phase scan: copy before, merge overlap, copy after; O(n).\n"
        "• Non-overlapping intervals (minimum removals) — sort by end; greedy keep earliest-ending non-conflicting.\n"
        "• Meeting Rooms I (can attend all?) — sort by start; check if any consecutive pair overlaps.\n"
        "• Meeting Rooms II (minimum rooms) — min-heap of end times; heap size is the answer.\n"
        "• Minimum Interval per Query — offline: sort queries and intervals; min-heap of (length, end)."
    ),
    "pitfalls": (
        "• Always sort by start time first.\n"
        "• Merge: use max(current.end, next.end) — next may be fully contained inside current.\n"
        "• Insert Interval: overlap condition is intervals[i][0] <= new_interval[1] (≤, not <).\n"
        "• Non-overlapping (remove minimum): sort by END, not start."
    ),
    "edge_cases": (
        "• Empty input — return [] immediately; merged[0] initialisation crashes without a guard.\n"
        "• Single interval — no merging; return as-is.\n"
        "• Touching intervals ([1,3] and [3,5]) — condition ≤ merges them into [1,5]; change to < if problem says 'touching' is non-overlap.\n"
        "• Fully contained ([1,10] contains [3,5]) — max(current.end, next.end) handles this correctly."
    ),
    "confusion": (
        "┌─────────────────────┬───────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Greedy (general)    │ Specifically merging/counting/scheduling [s,e] pairs? │\n"
        "│                     │ → Intervals pattern. Broader optimisation with a      │\n"
        "│                     │ greedy proof? → Greedy.                               │\n"
        "├─────────────────────┼───────────────────────────────────────────────────────┤\n"
        "│ Sliding Window      │ 'Intervals' defined by array indices + constraint?    │\n"
        "│                     │ → Sliding Window. Arbitrary [start,end] pairs?        │\n"
        "│                     │ → Intervals.                                          │\n"
        "└─────────────────────┴───────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you solve Meeting Rooms II without a heap?\n"
        "• What if intervals have equal start times — does merge still work?\n"
        "• Insert Interval is O(n) — can you do O(log n)?"
    ),
    "time": "O(n log n)",
    "space": "O(n)",
    "problems": [
        ("Merge Intervals",                        "M"),
        ("Insert Interval",                        "M"),
        ("Non-overlapping Intervals",              "M"),
        ("Meeting Rooms",                          "E"),
        ("Meeting Rooms II",                       "M"),
        ("Minimum Interval to Include Each Query", "H"),
    ],
    "related": ["Greedy", "Heap / Priority Queue"],
}
