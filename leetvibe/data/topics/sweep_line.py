from __future__ import annotations

TOPIC: dict = {
    "title": "Sweep Line",
    "slug": "Sweep Line",
    "recognize": (
        "Event at a point in time, number of overlapping intervals at any moment, skyline problem,\n"
        "meeting rooms, car pooling, count concurrent events, maximum overlap.\n"
        "Keywords: the answer depends on the state of the timeline AT EVERY POINT, not just per-interval."
    ),
    "intuition": (
        "• Instead of asking 'does interval A overlap interval B' pairwise (O(n²)), convert each\n"
        "  interval into two EVENTS (start, end) and sort them — the active count only changes at\n"
        "  event points, so scanning events in time order tracks the true state cheaply.\n"
        "• Sorting (time, delta) as tuples resolves ties automatically: Python compares the second\n"
        "  element when times match, so encoding end=-1 before start=+1 processes departures first.\n"
        "• This is the same idea as a difference array, just applied to continuous/event time\n"
        "  instead of discrete array indices."
    ),
    "diagram": (
        "  Events (start=+1, end=-1) sorted by time:\n"
        "\n"
        "  Intervals: [1,5]  [2,4]  [3,7]\n"
        "  Events:  (1,+1) (2,+1) (3,+1) (4,-1) (5,-1) (7,-1)\n"
        "\n"
        "  Sweep:\n"
        "  t=1: active=1   t=2: active=2   t=3: active=3  ← peak\n"
        "  t=4: active=2   t=5: active=1   t=7: active=0\n"
        "\n"
        "  Maximum simultaneous overlap = 3\n"
        "\n"
        "  Key: on tie (same time), process END events before START events\n"
        "  (or START before END depending on whether endpoints are inclusive)."
    ),
    "patterns": [
        {
            "name": "Maximum simultaneous overlapping intervals",
            "code": (
                "events = []\n"
                "for start, end in intervals:\n"
                "    events.append((start,  1))   # start event\n"
                "    events.append((end,   -1))   # end event\n"
                "events.sort()                    # ties: -1 (end) before +1 (start)\n"
                "                                 # because Python sorts tuples lexicographically\n"
                "                                 # (t, -1) < (t, +1) — ends processed first\n"
                "active = max_active = 0\n"
                "for _, delta in events:\n"
                "    active += delta\n"
                "    max_active = max(max_active, active)\n"
                "return max_active"
            ),
        },
        {
            "name": "Car Pooling — difference array variant of sweep line",
            "code": (
                "# trips: (passengers, from, to); capacity: max passengers\n"
                "stops = [0] * 1001   # difference array over stop indices\n"
                "for passengers, start, end in trips:\n"
                "    stops[start] += passengers\n"
                "    stops[end]   -= passengers    # passengers exit at 'end'\n"
                "\n"
                "current = 0\n"
                "for delta in stops:\n"
                "    current += delta\n"
                "    if current > capacity:\n"
                "        return False\n"
                "return True\n"
                "\n"
                "# Count of Buildings in Each Query (sorted events + bisect)\n"
                "# General pattern: sort queries and events together, process in order\n"
                "import bisect\n"
                "\n"
                "def count_covered(intervals, queries):\n"
                "    # For each query point, count how many intervals cover it\n"
                "    starts = sorted(s for s, _ in intervals)\n"
                "    ends   = sorted(e for _, e in intervals)\n"
                "    result = []\n"
                "    for q in queries:\n"
                "        # intervals that started <= q minus those that ended < q\n"
                "        started = bisect.bisect_right(starts, q)\n"
                "        ended   = bisect.bisect_left(ends, q)\n"
                "        result.append(started - ended)\n"
                "    return result"
            ),
        },
    ],
    "variants": (
        "• Max concurrent overlap (Meeting Rooms II) — (time, ±1) events; track running active count.\n"
        "• Difference array sweep (Car Pooling) — discrete stop/day indices instead of raw timestamps.\n"
        "• Skyline problem — events carry a height; track a multiset/heap of active heights, not just a count.\n"
        "• Query-based sweep (count covered at query points) — sort events and queries together,\n"
        "  process in time order, or bisect against sorted starts/ends.\n"
        "• Heap alternative (Meeting Rooms II) — min-heap of end times; push/pop instead of sorting\n"
        "  all events, same O(n log n) but no explicit event list."
    ),
    "pitfalls": (
        "• Tie-breaking at the same timestamp matters: whether an ending and starting event at the\n"
        "  same time overlap depends on whether intervals are open or closed — read carefully.\n"
        "• Difference array sweep: mark +delta at start, -delta at end (not end+1 for continuous\n"
        "  time — check if indices are discrete or continuous).\n"
        "• Sorting events as tuples (time, delta) handles ties automatically: (t, -1) sorts before\n"
        "  (t, +1) so ends are processed first."
    ),
    "edge_cases": (
        "• No intervals — max_active stays 0.\n"
        "• All intervals identical — max_active equals the total count of intervals.\n"
        "• Point intervals (start == end) — decide whether they count as overlapping instantly or not.\n"
        "• Intervals touching at endpoints ([1,3] and [3,5]) — tie-break order determines whether\n"
        "  they're treated as overlapping."
    ),
    "confusion": (
        "┌───────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with   │ Distinguishing question                              │\n"
        "├───────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Heap / Priority Queue │ Just need the max concurrent count, no per-event     │\n"
        "│                       │ detail? → Sweep Line (sort events). Need to actively │\n"
        "│                       │ track and reuse specific resources (which room is    │\n"
        "│                       │ free)? → Heap of end times.                          │\n"
        "└───────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• How would you solve Meeting Rooms II with a heap instead of sorted events?\n"
        "• What changes if intervals are half-open [start, end) vs closed [start, end]?\n"
        "• How would you extend this to report WHICH intervals overlap at the peak, not just the count?\n"
        "• Can you answer 'how many events active at time T' for arbitrary query T efficiently?"
    ),
    "time": "O(n log n)  sorting events",
    "space": "O(n)  events list  /  O(k)  difference array (k = range size)",
    "problems": [
        ("Car Pooling",                     "M"),
        ("Corporate Flight Bookings",       "M"),
        ("Count Ways to Group Overlaps",    "H"),
        ("My Calendar II",                  "M"),
    ],
    "related": ["Intervals", "Greedy", "Prefix Sum", "Heap / Priority Queue"],
}
