from __future__ import annotations

TOPIC: dict = {
    "title": "Reservoir Sampling",
    "slug": "Reservoir Sampling",
    "recognize": (
        "\"random pick\" from unknown-length stream, \"random node in linked list\",\n"
        "  uniform random sample without knowing n upfront."
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
    "when": (
        "Random sampling from a stream or linked list of unknown / very large size,\n"
        "  where you cannot store all elements in memory."
    ),
    "pattern": (
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
    "pattern2": (
        "# Random Node in a Linked List\n"
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
    "pitfalls": (
        "• Replace with probability 1/count (not 1/i) — count only tracks\n"
        "  occurrences of the target, not all elements seen.\n"
        "• k-reservoir: replace reservoir[j] only when j < k — not just any j.\n"
        "• The random.randint(1, count) == 1 idiom is equivalent to\n"
        "  random.random() < 1/count — either form is correct."
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
