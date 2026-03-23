from __future__ import annotations

from ._selector import TOPIC as _t0
from .array import TOPIC as _t1
from .prefix_sum import TOPIC as _t2
from .two_pointers import TOPIC as _t3
from .sliding_window import TOPIC as _t4
from .stack import TOPIC as _t5
from .monotonic_stack import TOPIC as _t6
from .binary_search import TOPIC as _t7
from .linked_list import TOPIC as _t8
from .tree import TOPIC as _t9
from .trie import TOPIC as _t10
from .heap import TOPIC as _t11
from .graph import TOPIC as _t12
from .matrix import TOPIC as _t13
from .union_find import TOPIC as _t14
from .topological_sort import TOPIC as _t15
from .dijkstra import TOPIC as _t16
from .backtracking import TOPIC as _t17
from .dynamic_programming import TOPIC as _t18
from .greedy import TOPIC as _t19
from .intervals import TOPIC as _t20
from .bit_manipulation import TOPIC as _t21
from .math import TOPIC as _t22
from .modified_binary_search import TOPIC as _t23
from .fast_slow_pointers import TOPIC as _t24
from .bellman_ford import TOPIC as _t25
from .segment_tree import TOPIC as _t26
from .cyclic_sort import TOPIC as _t27
from .queue import TOPIC as _t28
from .monotonic_queue import TOPIC as _t29
from .merge_sort import TOPIC as _t30
from .string import TOPIC as _t31
from .reservoir_sampling import TOPIC as _t32
from .lru_cache import TOPIC as _t33
from .sorting import TOPIC as _t34
from .mst import TOPIC as _t35
from .floyd_warshall import TOPIC as _t36
from .sweep_line import TOPIC as _t37
from .rabin_karp import TOPIC as _t38
from .sorted_list import TOPIC as _t39
from .iterator import TOPIC as _t40
from .scc import TOPIC as _t41
from .eulerian import TOPIC as _t42
from .digit_dp import TOPIC as _t43
from .probability_dp import TOPIC as _t44
from .game_theory import TOPIC as _t45
from .z_algorithm import TOPIC as _t46
from .network_flow import TOPIC as _t47
from .difference_array import TOPIC as _t48
from .manacher import TOPIC as _t49
from .bfs_01 import TOPIC as _t50
from .simulation import TOPIC as _t51
from .concurrency import TOPIC as _t52

TOPICS: list[dict] = [
    _t0, _t1, _t2, _t3, _t4, _t5, _t6, _t7, _t8, _t9,
    _t10, _t11, _t12, _t13, _t14, _t15, _t16, _t17, _t18, _t19,
    _t20, _t21, _t22, _t23, _t24, _t25, _t26, _t27, _t28, _t29,
    _t30, _t31, _t32, _t33, _t34, _t35, _t36, _t37, _t38, _t39,
    _t40, _t41, _t42, _t43, _t44, _t45, _t46, _t47, _t48, _t49,
    _t50, _t51, _t52,
]

# ═══════════════════════════════════════════════════════════════════════════
# CATEGORY & TIER METADATA
# ═══════════════════════════════════════════════════════════════════════════
# category : display group for sidebar navigation
# tier     : 1=foundational, 2=intermediate, 3=advanced/FAANG
# parent   : title of the parent topic this is a specialisation of (or "")
#
# Inject into each topic dict via the TOPIC_META mapping below,
# or read CATEGORIES / TIER_MAP directly for sidebar rendering.

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
    # ── Dynamic Programming ───────────────────────────────────────────────
    "Dynamic Programming":              {"category": "Dynamic Prog.",    "tier": 1, "parent": ""},
    "Greedy":                           {"category": "Dynamic Prog.",    "tier": 2, "parent": "Dynamic Programming"},
    "Intervals":                        {"category": "Dynamic Prog.",    "tier": 2, "parent": "Greedy"},
    # ── Heap & Sorting ────────────────────────────────────────────────────
    "Heap / Priority Queue":            {"category": "Heap & Sorting",   "tier": 1, "parent": ""},
    "Merge Sort / Divide & Conquer":    {"category": "Heap & Sorting",   "tier": 2, "parent": ""},
    "Segment Tree":                     {"category": "Heap & Sorting",   "tier": 3, "parent": "Prefix Sum"},
    # ── Strings ───────────────────────────────────────────────────────────
    "String Manipulation":              {"category": "Strings",          "tier": 1, "parent": ""},
    "Rabin-Karp":                       {"category": "Strings",          "tier": 3, "parent": "String Manipulation"},
    # ── Math & Bits ───────────────────────────────────────────────────────
    "Math Patterns":                    {"category": "Math & Bits",      "tier": 2, "parent": ""},
    "Bit Manipulation":                 {"category": "Math & Bits",      "tier": 2, "parent": ""},
    # ── Misc Patterns ─────────────────────────────────────────────────────
    "Backtracking":                     {"category": "Misc Patterns",    "tier": 1, "parent": ""},
    "Sweep Line":                       {"category": "Misc Patterns",    "tier": 2, "parent": "Intervals"},
    "Reservoir Sampling":               {"category": "Misc Patterns",    "tier": 3, "parent": ""},
    # ── New topics ────────────────────────────────────────────────────────
    "Ordered Set / SortedList":         {"category": "Heap & Sorting",   "tier": 2, "parent": "Heap / Priority Queue"},
    "Iterator Design Pattern":          {"category": "Misc Patterns",    "tier": 2, "parent": ""},
    "Strongly Connected Components":    {"category": "Graphs",           "tier": 3, "parent": "Graphs"},
    "Eulerian Path / Circuit":          {"category": "Graphs",           "tier": 3, "parent": "Graphs"},
    "Digit DP":                         {"category": "Dynamic Prog.",    "tier": 3, "parent": "Dynamic Programming"},
    "Probability DP":                   {"category": "Dynamic Prog.",    "tier": 3, "parent": "Dynamic Programming"},
    "Game Theory":                      {"category": "Math & Bits",      "tier": 3, "parent": ""},
    "Z-Algorithm":                      {"category": "Strings",          "tier": 3, "parent": "String Manipulation"},
    "Network Flow":                     {"category": "Graphs",           "tier": 3, "parent": "Graphs"},
    # ── v7 additions ──────────────────────────────────────────────────────
    "Difference Array":                 {"category": "Arrays",           "tier": 2, "parent": "Prefix Sum"},
    "Manacher's Algorithm":             {"category": "Strings",          "tier": 3, "parent": "String Manipulation"},
    "0-1 BFS":                          {"category": "Graphs",           "tier": 2, "parent": "Graphs"},
    "Simulation":                       {"category": "Misc Patterns",    "tier": 1, "parent": ""},
    "Concurrency":                      {"category": "Misc Patterns",    "tier": 3, "parent": ""},
}

# Enrich every TOPICS entry with category / tier / parent in-place
for _t in TOPICS:
    _m = TOPIC_META.get(_t["title"], {"category": "Misc Patterns", "tier": 2, "parent": ""})
    _t["category"] = _m["category"]
    _t["tier"]     = _m["tier"]
    _t["parent"]   = _m["parent"]

# ── Ordered category list for sidebar rendering ────────────────────────────
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
