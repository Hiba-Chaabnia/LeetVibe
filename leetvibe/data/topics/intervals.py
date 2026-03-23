from __future__ import annotations

TOPIC: dict = {
    "title": "Intervals",
    "slug": "Intervals",
    "recognize": (
        "\"overlapping\", \"scheduling\", \"meeting rooms\", \"insert interval\",\n"
        "  \"merge ranges\", \"minimum intervals to remove\"."
    ),
    "diagram": (
        "  Merge overlapping intervals:\n"
        "  input:   [1──3]  [2────5]  [6──8]  [9─10]\n"
        "  sort by start, merge if next.start <= current.end:\n"
        "  output:  [1────────5]      [6──8]  [9─10]\n"
        "\n"
        "  overlap condition:  next.start  <=  current.end"
    ),
    "when": (
        "Scheduling, calendar conflicts, merging ranges,\n"
        "  or finding the minimum coverage / number of rooms needed."
    ),
    "pattern": (
        "# Merge intervals\n"
        "intervals.sort(key=lambda x: x[0])\n"
        "merged = [intervals[0]]\n"
        "for start, end in intervals[1:]:\n"
        "    if start <= merged[-1][1]:           # overlapping\n"
        "        merged[-1][1] = max(merged[-1][1], end)\n"
        "    else:\n"
        "        merged.append([start, end])\n"
        "return merged"
    ),
    "pattern2": (
        "# Insert Interval — 3-phase: before / overlap / after\n"
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
    "pitfalls": (
        "• Always sort by start time first.\n"
        "• Merge: use max(current.end, next.end) — next may be fully contained.\n"
        "• Insert Interval: overlap condition is intervals[i][0] <= new_interval[1]\n"
        "  (strictly ≤, not <) — adjacent intervals that touch should merge.\n"
        "• Non-overlapping (remove minimum): sort by end, greedy keep earliest-ending."
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
