from __future__ import annotations

TOPIC: dict = {
    "title": "Reservoir Sampling",
    "slug": "Reservoir Sampling",
    "recognize": (
        "Random pick from a stream or linked list of unknown length.\n"
        "Uniform random sample without knowing n upfront, O(1) space.\n"
        "Signal: 'random node', 'random index', stream of unbounded size."
    ),
    "intuition": (
        "• Invariant: after seeing i elements, the reservoir holds a uniform random\n"
        "  sample — each element has probability 1/i of being chosen.\n"
        "• At element i, replace the current choice with probability 1/i.\n"
        "  This preserves the invariant: P(earlier element j survives) = (1/i) × (i/(i+1)) = 1/(i+1).\n"
        "• For k-reservoir: replace with probability k/(i+1) instead; fill first k greedily."
    ),
    "diagram": (
        "  Stream: [a, b, c, d, e, ...]  — length N unknown\n"
        "\n"
        "  Algorithm (k=1 reservoir):\n"
        "  i=1: pick a  with prob 1/1   → reservoir = [a]\n"
        "  i=2: pick b  with prob 1/2   → reservoir = [a or b]\n"
        "  i=3: pick c  with prob 1/3   → replace current with prob 1/3\n"
        "  i=4: pick d  with prob 1/4   → replace current with prob 1/4\n"
        "  ...\n"
        "  After N items: every element has been chosen with prob 1/N  ✓\n"
        "\n"
        "  Proof: P(item i survives to end) = (1/i) × (i/(i+1)) × ... = 1/N"
    ),
    "patterns": [
        {
            "name": "Random Pick Index — pick one uniform random index where nums[i] == target",
            "code": (
                "import random\n"
                "\n"
                "# Random Pick Index — pick one uniform random index where nums[i] == target\n"
                "class Solution:\n"
                "    def __init__(self, nums):\n"
                "        self.nums = nums\n"
                "\n"
                "    def pick(self, target):\n"
                "        count = result = 0\n"
                "        for i, num in enumerate(self.nums):\n"
                "            if num == target:\n"
                "                count += 1\n"
                "                if random.randint(1, count) == 1:  # replace with prob 1/count\n"
                "                    result = i\n"
                "        return result"
            ),
        },
        {
            "name": "Random Node in a Linked List",
            "code": (
                "import random\n"
                "\n"
                "class Solution:\n"
                "    def __init__(self, head):\n"
                "        self.head = head\n"
                "\n"
                "    def get_random(self):\n"
                "        scope  = 1\n"
                "        chosen = None\n"
                "        curr   = self.head\n"
                "        while curr:\n"
                "            if random.randint(1, scope) == 1:  # replace with prob 1/scope\n"
                "                chosen = curr.val\n"
                "            curr  = curr.next\n"
                "            scope += 1\n"
                "        return chosen\n"
                "\n"
                "# k-reservoir (keep k items, each with equal probability k/N)\n"
                "def reservoir_sample(stream, k):\n"
                "    reservoir = []\n"
                "    for i, item in enumerate(stream):\n"
                "        if i < k:\n"
                "            reservoir.append(item)\n"
                "        else:\n"
                "            j = random.randint(0, i)     # random index in [0, i]\n"
                "            if j < k:\n"
                "                reservoir[j] = item      # replace with prob k/(i+1)\n"
                "    return reservoir"
            ),
        },
    ],
    "variants": (
        "• k=1 (single pick) — replace with prob 1/count; for Random Pick Index / Linked List.\n"
        "• k-reservoir — fill first k; for element i ≥ k, replace reservoir[j] if j < k.\n"
        "• Weighted reservoir (Efraimidis-Spirakis) — key = uniform^(1/weight); keep k largest keys.\n"
        "• Random Pick with Weight — prefix sum + binary search on random value; O(log n) per pick."
    ),
    "pitfalls": (
        "• Replace with 1/count (not 1/i) — count tracks only target occurrences, not all elements.\n"
        "• k-reservoir: replace reservoir[j] only when j < k.\n"
        "• random.randint(1, count)==1 is equivalent to random.random() < 1/count — either is correct."
    ),
    "edge_cases": (
        "• Empty stream — reservoir is empty; return None or guard at call site.\n"
        "• target never appears in Random Pick Index — problem guarantees it exists; guard if not.\n"
        "• k > stream length — reservoir fills from the first k; else branch never runs; still correct."
    ),
    "confusion": (
        "┌─────────────────────────┬──────────────────────────────────────────────────┐\n"
        "│ Often confused with     │ Distinguishing question                          │\n"
        "├─────────────────────────┼──────────────────────────────────────────────────┤\n"
        "│ Fisher-Yates shuffle    │ Full array in memory? → Shuffle in-place O(n).   │\n"
        "│                         │ Stream of unknown length? → Reservoir sampling.  │\n"
        "├─────────────────────────┼──────────────────────────────────────────────────┤\n"
        "│ Random Pick with Weight │ All elements equally likely? → Reservoir.        │\n"
        "│                         │ Different weights? → Prefix sum + binary search. │\n"
        "└─────────────────────────┴──────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Prove that reservoir sampling is uniformly random.\n"
        "• How would you sample k elements instead of 1?\n"
        "• What if elements have different weights and you want weighted sampling from a stream?"
    ),
    "time": "O(n)  single pass through stream",
    "space": "O(1)  (O(k) for k-reservoir)",
    "problems": [
        ("Random Pick Index",           "M"),
        ("Linked List Random Node",     "M"),
        ("Random Pick with Weight",     "M"),
        ("Shuffle an Array",            "M"),
    ],
    "related": ["Linked List", "Math Patterns"],
}
