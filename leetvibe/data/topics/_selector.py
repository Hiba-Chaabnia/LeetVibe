from __future__ import annotations

TOPIC: dict = {
    "title": "▶  Pattern Selector",
    "slug": "_selector",
    "recognize": "",
    "diagram": (
        "  Read the problem statement. Match keywords to a pattern:\n"
        "\n"
        "  KEYWORD / CONSTRAINT                        PATTERN\n"
        "  ─────────────────────────────────────────────────────────────\n"
        "  \"contiguous subarray\"                     → Sliding Window\n"
        "  sorted array + pair / triplet              → Two Pointers\n"
        "  sorted + find value / O(log n)             → Binary Search\n"
        "  rotated array / find boundary index        → Modified Binary Search\n"
        "  \"minimum / maximum valid answer\"           → Binary Search (answer space)\n"
        "  range sum / subarray sum = k               → Prefix Sum\n"
        "  all combinations / permutations / subsets  → Backtracking\n"
        "  shortest path, unweighted graph            → BFS (Graphs)\n"
        "  shortest path, weighted (≥ 0)              → Dijkstra\n"
        "  shortest path + negative edge weights      → Bellman-Ford\n"
        "  \"connected\" / \"same group\" / merge         → Union Find\n"
        "  prerequisites / dependency order           → Topological Sort\n"
        "  next greater / next smaller element        → Monotonic Stack\n"
        "  top-K / streaming median / two-halves      → Heap\n"
        "  prefix / autocomplete / word search        → Trie\n"
        "  overlapping subproblems + count/min        → Dynamic Programming\n"
        "  local choice → global optimum              → Greedy\n"
        "  scheduling / overlapping ranges            → Intervals\n"
        "  grid / matrix / island / flood fill        → Matrix / Grid\n"
        "  unique element / XOR trick                 → Bit Manipulation\n"
        "  prime / GCD / power / modular math         → Math Patterns\n"
        "  cycle in linked list / duplicate number    → Fast & Slow Pointers\n"
        "  range queries on MUTABLE array             → Segment Tree / Fenwick\n"
        "  missing / duplicate in [1..n] range        → Cyclic Sort\n"
        "  \"bipartite\" / \"2-colorable\" / two groups   → Graphs (BFS color check)\n"
        "  \"stream of numbers\" / running statistic    → Heap (two-heaps)\n"
        "  \"in-place\" / \"O(1) extra space\"            → Cyclic Sort or Two Pointers\n"
        "  \"serialize\" / \"deserialize\" / encode       → Trees or Tries\n"
        "  \"find pattern in text\" / O(n+m) match     → String Manipulation (KMP)\n"
        "  \"path through tree\" / \"value passed up\"   → Trees (Tree DP post-order)\n"
        "  \"k[encoded_string]\" / nested decode        → Simulation (stack parser)\n"
    ),
    "when": (
        "Start here when you don't immediately recognise the pattern.\n"
        "  Scan for keywords, then jump to the matching topic."
    ),
    "pattern": "",
    "pattern2": "",
    "pitfalls": "",
    "time": "",
    "space": "",
    "problems": [],
    "related": [],
}
