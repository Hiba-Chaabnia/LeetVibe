from __future__ import annotations

TOPIC: dict = {
    "title": "Sweep Line",
    "slug": "Sweep Line",
    "recognize": (
        "\"event at a point in time\", \"number of overlapping intervals at any moment\",\n"
        "  \"skyline problem\", \"meeting rooms\", \"car pooling\",\n"
        "  \"count concurrent events\", \"maximum overlap\"."
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
    "when": (
        "Any problem asking about the state at every point in a timeline:\n"
        "  maximum simultaneous events, coverage gaps, the skyline profile,\n"
        "  or whether a new event fits without overlap."
    ),
    "pattern": (
        "# Maximum simultaneous overlapping intervals\n"
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
    "pattern2": (
        "# Car Pooling — difference array variant of sweep line\n"
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
    "pitfalls": (
        "• Tie-breaking at the same timestamp matters: whether an ending and a\n"
        "  starting event at the same time create an overlap depends on whether\n"
        "  intervals are open or closed — read the problem carefully.\n"
        "• Difference array sweep: mark +delta at start, -delta at end (not end+1\n"
        "  for continuous time — check if indices are discrete or continuous).\n"
        "• Sorting events as tuples (time, delta) handles ties automatically:\n"
        "  (t, -1) sorts before (t, +1) so ends are processed first."
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
