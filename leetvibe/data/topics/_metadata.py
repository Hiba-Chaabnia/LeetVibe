"""Topic metadata: category groupings, tier levels, and parent relationships."""

from __future__ import annotations

TOPIC_META: dict[str, dict] = {
    "▶  Pattern Selector":             {"category": "_nav",             "tier": 1, "parent": ""},
    # ── Arrays ────────────────────────────────────────────────────────────
    "Arrays & Hashing":                {"category": "Arrays",           "tier": 1, "parent": ""},
    "Prefix Sum":                       {"category": "Arrays",           "tier": 1, "parent": "Arrays & Hashing"},
    "Two Pointers":                     {"category": "Arrays",           "tier": 1, "parent": "Arrays & Hashing"},
    "Sliding Window":                   {"category": "Arrays",           "tier": 1, "parent": "Arrays & Hashing"},
    "Cyclic Sort":                      {"category": "Arrays",           "tier": 2, "parent": "Arrays & Hashing"},
    "Sorting Algorithms":               {"category": "Arrays",           "tier": 2, "parent": ""},
    # ── Stack & Queue ─────────────────────────────────────────────────────
    "Stack":                            {"category": "Stack & Queue",    "tier": 1, "parent": ""},
    "Queue":                            {"category": "Stack & Queue",    "tier": 1, "parent": "Stack"},
    "Monotonic Stack":                  {"category": "Stack & Queue",    "tier": 2, "parent": "Stack"},
    "Monotonic Queue":                  {"category": "Stack & Queue",    "tier": 2, "parent": "Queue"},
    # ── Linked List ───────────────────────────────────────────────────────
    "Linked List":                      {"category": "Linked List",      "tier": 1, "parent": ""},
    "Fast & Slow Pointers":             {"category": "Linked List",      "tier": 2, "parent": "Linked List"},
    "LRU Cache":                        {"category": "Linked List",      "tier": 2, "parent": "Linked List"},
    # ── Binary Search ─────────────────────────────────────────────────────
    "Binary Search":                    {"category": "Binary Search",    "tier": 1, "parent": ""},
    "Modified Binary Search":           {"category": "Binary Search",    "tier": 2, "parent": "Binary Search"},
    # ── Trees & Tries ─────────────────────────────────────────────────────
    "Trees":                            {"category": "Trees & Tries",    "tier": 1, "parent": ""},
    "Tries":                            {"category": "Trees & Tries",    "tier": 2, "parent": "Trees"},
    # ── Graphs ────────────────────────────────────────────────────────────
    "Graphs":                           {"category": "Graphs",           "tier": 1, "parent": ""},
    "Matrix / Grid":                    {"category": "Graphs",           "tier": 1, "parent": "Graphs"},
    "Union Find":                       {"category": "Graphs",           "tier": 2, "parent": "Graphs"},
    "Topological Sort":                 {"category": "Graphs",           "tier": 2, "parent": "Graphs"},
    "Dijkstra":                         {"category": "Graphs",           "tier": 2, "parent": "Graphs"},
    "Bellman-Ford":                     {"category": "Graphs",           "tier": 3, "parent": "Dijkstra"},
    "Minimum Spanning Tree":            {"category": "Graphs",           "tier": 2, "parent": "Graphs"},
    "Floyd-Warshall":                   {"category": "Graphs",           "tier": 3, "parent": "Dijkstra"},
    "Strongly Connected Components":    {"category": "Graphs",           "tier": 3, "parent": "Graphs"},
    "Eulerian Path / Circuit":          {"category": "Graphs",           "tier": 3, "parent": "Graphs"},
    "Network Flow":                     {"category": "Graphs",           "tier": 3, "parent": "Graphs"},
    "0-1 BFS":                          {"category": "Graphs",           "tier": 2, "parent": "Graphs"},
    # ── Dynamic Programming ───────────────────────────────────────────────
    "Dynamic Programming":              {"category": "Dynamic Prog.",    "tier": 1, "parent": ""},
    "Greedy":                           {"category": "Dynamic Prog.",    "tier": 2, "parent": "Dynamic Programming"},
    "Intervals":                        {"category": "Dynamic Prog.",    "tier": 2, "parent": "Greedy"},
    "Digit DP":                         {"category": "Dynamic Prog.",    "tier": 3, "parent": "Dynamic Programming"},
    "Probability DP":                   {"category": "Dynamic Prog.",    "tier": 3, "parent": "Dynamic Programming"},
    # ── Heap & Sorting ────────────────────────────────────────────────────
    "Heap / Priority Queue":            {"category": "Heap & Sorting",   "tier": 1, "parent": ""},
    "Merge Sort / Divide & Conquer":    {"category": "Heap & Sorting",   "tier": 2, "parent": ""},
    "Segment Tree":                     {"category": "Heap & Sorting",   "tier": 3, "parent": "Prefix Sum"},
    "Ordered Set / SortedList":         {"category": "Heap & Sorting",   "tier": 2, "parent": "Heap / Priority Queue"},
    # ── Strings ───────────────────────────────────────────────────────────
    "String Manipulation":              {"category": "Strings",          "tier": 1, "parent": ""},
    "Rabin-Karp":                       {"category": "Strings",          "tier": 3, "parent": "String Manipulation"},
    "Z-Algorithm":                      {"category": "Strings",          "tier": 3, "parent": "String Manipulation"},
    "Manacher's Algorithm":             {"category": "Strings",          "tier": 3, "parent": "String Manipulation"},
    # ── Math & Bits ───────────────────────────────────────────────────────
    "Math Patterns":                    {"category": "Math & Bits",      "tier": 2, "parent": ""},
    "Bit Manipulation":                 {"category": "Math & Bits",      "tier": 2, "parent": ""},
    "Game Theory":                      {"category": "Math & Bits",      "tier": 3, "parent": ""},
    # ── Misc Patterns ─────────────────────────────────────────────────────
    "Backtracking":                     {"category": "Misc Patterns",    "tier": 1, "parent": ""},
    "Sweep Line":                       {"category": "Misc Patterns",    "tier": 2, "parent": "Intervals"},
    "Reservoir Sampling":               {"category": "Misc Patterns",    "tier": 3, "parent": ""},
    "Iterator Design Pattern":          {"category": "Misc Patterns",    "tier": 2, "parent": ""},
    "Simulation":                       {"category": "Misc Patterns",    "tier": 1, "parent": ""},
    "Concurrency":                      {"category": "Misc Patterns",    "tier": 3, "parent": ""},
    # ── Difference Array ──────────────────────────────────────────────────
    "Difference Array":                 {"category": "Arrays",           "tier": 2, "parent": "Prefix Sum"},
}

CATEGORIES: list[dict] = [
    {"name": "Arrays",         "icon": "▦", "topics": [
        "Arrays & Hashing", "Two Pointers", "Sliding Window",
        "Prefix Sum", "Difference Array", "Cyclic Sort", "Sorting Algorithms"]},
    {"name": "Stack & Queue",  "icon": "⊟", "topics": [
        "Stack", "Queue", "Monotonic Stack", "Monotonic Queue"]},
    {"name": "Linked List",    "icon": "⛓", "topics": [
        "Linked List", "Fast & Slow Pointers", "LRU Cache"]},
    {"name": "Binary Search",  "icon": "⌖", "topics": [
        "Binary Search", "Modified Binary Search"]},
    {"name": "Trees & Tries",  "icon": "🌲", "topics": [
        "Trees", "Tries"]},
    {"name": "Graphs",         "icon": "◈", "topics": [
        "Graphs", "Matrix / Grid", "Union Find", "Topological Sort",
        "Dijkstra", "0-1 BFS", "Bellman-Ford",
        "Minimum Spanning Tree", "Floyd-Warshall",
        "Strongly Connected Components", "Eulerian Path / Circuit",
        "Network Flow"]},
    {"name": "Dynamic Prog.",  "icon": "⧠", "topics": [
        "Dynamic Programming", "Greedy", "Intervals",
        "Digit DP", "Probability DP"]},
    {"name": "Heap & Sorting", "icon": "△", "topics": [
        "Heap / Priority Queue", "Merge Sort / Divide & Conquer",
        "Segment Tree", "Ordered Set / SortedList"]},
    {"name": "Strings",        "icon": "❝", "topics": [
        "String Manipulation", "Rabin-Karp", "Z-Algorithm",
        "Manacher's Algorithm"]},
    {"name": "Math & Bits",    "icon": "∑", "topics": [
        "Math Patterns", "Bit Manipulation", "Game Theory"]},
    {"name": "Misc Patterns",  "icon": "◎", "topics": [
        "Backtracking", "Sweep Line", "Simulation",
        "Iterator Design Pattern", "Reservoir Sampling", "Concurrency"]},
]

TIER_MAP: dict[int, list[str]] = {
    1: ["Arrays & Hashing", "Two Pointers", "Sliding Window", "Prefix Sum",
        "Stack", "Queue", "Linked List", "Binary Search", "Trees", "Graphs",
        "Matrix / Grid", "Dynamic Programming", "Backtracking",
        "Heap / Priority Queue", "String Manipulation", "Simulation"],
    2: ["Monotonic Stack", "Monotonic Queue", "Fast & Slow Pointers", "LRU Cache",
        "Modified Binary Search", "Tries", "Union Find", "Topological Sort",
        "Dijkstra", "0-1 BFS", "Minimum Spanning Tree", "Greedy", "Intervals",
        "Merge Sort / Divide & Conquer", "Bit Manipulation", "Math Patterns",
        "Cyclic Sort", "Sorting Algorithms", "Sweep Line", "Difference Array",
        "Ordered Set / SortedList", "Iterator Design Pattern"],
    3: ["Bellman-Ford", "Floyd-Warshall", "Strongly Connected Components",
        "Eulerian Path / Circuit", "Network Flow", "Segment Tree",
        "Digit DP", "Probability DP", "Game Theory",
        "Rabin-Karp", "Z-Algorithm", "Manacher's Algorithm",
        "Reservoir Sampling", "Concurrency"],
}
