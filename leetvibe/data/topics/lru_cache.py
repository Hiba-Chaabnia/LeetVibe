from __future__ import annotations

TOPIC: dict = {
    "title": "LRU Cache",
    "slug": "LRU Cache",
    "recognize": (
        "LRU cache, most recently used, evict least recently used, O(1) get and put with bounded capacity.\n"
        "Signal: 'design a cache' — hash map for O(1) lookup, doubly linked list for O(1) eviction."
    ),
    "intuition": (
        "• Hash map gives O(1) lookup by key → node; doubly linked list gives O(1) removal at any position.\n"
        "• Every get and put moves the accessed node to the tail (MRU position) — the LRU is always at head.next.\n"
        "• Dummy head/tail sentinels eliminate all null-pointer edge cases for _remove and _insert_tail."
    ),
    "diagram": (
        "  Doubly Linked List + Hash Map:\n"
        "\n"
        "  head ↔ [1:A] ↔ [2:B] ↔ [3:C] ↔ tail\n"
        "  (LRU)                           (MRU)\n"
        "\n"
        "  hash: {1→nodeA, 2→nodeB, 3→nodeC}\n"
        "\n"
        "  get(2):  move B to tail   → head ↔ [1] ↔ [3] ↔ [2] ↔ tail\n"
        "  put(4):  evict head.next (node 1), insert 4 at tail\n"
        "           → head ↔ [3] ↔ [2] ↔ [4] ↔ tail"
    ),
    "patterns": [
        {
            "name": "LRU Cache (Doubly Linked List + Hash Map)",
            "code": (
                "class Node:\n"
                "    def __init__(self, key=0, val=0):\n"
                "        self.key, self.val  = key, val\n"
                "        self.prev = self.next = None\n"
                "\n"
                "class LRUCache:\n"
                "    def __init__(self, capacity):\n"
                "        self.cap   = capacity\n"
                "        self.cache = {}                    # key → node\n"
                "        self.head  = Node()                # dummy LRU sentinel\n"
                "        self.tail  = Node()                # dummy MRU sentinel\n"
                "        self.head.next = self.tail\n"
                "        self.tail.prev = self.head\n"
                "\n"
                "    def _remove(self, node):\n"
                "        node.prev.next = node.next\n"
                "        node.next.prev = node.prev\n"
                "\n"
                "    def _insert_tail(self, node):\n"
                "        node.prev         = self.tail.prev\n"
                "        node.next         = self.tail\n"
                "        self.tail.prev.next = node\n"
                "        self.tail.prev    = node\n"
                "\n"
                "    def get(self, key):\n"
                "        if key not in self.cache: return -1\n"
                "        node = self.cache[key]\n"
                "        self._remove(node); self._insert_tail(node)\n"
                "        return node.val\n"
                "\n"
                "    def put(self, key, value):\n"
                "        if key in self.cache:\n"
                "            self._remove(self.cache[key])\n"
                "        node = Node(key, value)\n"
                "        self.cache[key] = node\n"
                "        self._insert_tail(node)\n"
                "        if len(self.cache) > self.cap:\n"
                "            lru = self.head.next\n"
                "            self._remove(lru)\n"
                "            del self.cache[lru.key]"
            ),
        },
        {
            "name": "Python shortcut: OrderedDict",
            "code": (
                "from collections import OrderedDict\n"
                "\n"
                "class LRUCache:\n"
                "    def __init__(self, capacity):\n"
                "        self.cap   = capacity\n"
                "        self.cache = OrderedDict()\n"
                "\n"
                "    def get(self, key):\n"
                "        if key not in self.cache: return -1\n"
                "        self.cache.move_to_end(key)\n"
                "        return self.cache[key]\n"
                "\n"
                "    def put(self, key, value):\n"
                "        if key in self.cache:\n"
                "            self.cache.move_to_end(key)\n"
                "        self.cache[key] = value\n"
                "        if len(self.cache) > self.cap:\n"
                "            self.cache.popitem(last=False)  # evict LRU"
            ),
        },
    ],
    "variants": (
        "• LRU Cache — doubly linked list (LRU→MRU) + hash map (key→node); O(1) all ops.\n"
        "• LRU Cache (Python shortcut) — OrderedDict; move_to_end + popitem(last=False); acceptable in interviews.\n"
        "• LFU Cache — evict least FREQUENTLY used; two hash maps + min_freq tracker; significantly more complex.\n"
        "• All O(1) Data Structure (inc/dec/getMaxKey/getMinKey) — generalises the frequency-bucket idea."
    ),
    "pitfalls": (
        "• Always update both hash map AND linked list — forgetting del cache[lru.key] after eviction is a memory leak.\n"
        "• Dummy head/tail sentinels are mandatory — they prevent null-pointer edge cases for _remove.\n"
        "• OrderedDict is interview-acceptable, but interviewers often ask for the DLL implementation.\n"
        "• LFU (least FREQUENTLY used) needs two hash maps + freq tracking — not the same as LRU."
    ),
    "edge_cases": (
        "• capacity = 1 — every put evicts the previous entry (if different key).\n"
        "• put with an existing key (update) — move to MRU AND update value; forgetting the move causes stale ordering.\n"
        "• get on a non-existent key — return -1; do not insert or modify the list.\n"
        "• Eviction of the only element — sentinels make head ↔ tail re-linking automatic."
    ),
    "confusion": (
        "┌─────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                             │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ LFU Cache           │ Evict LEAST RECENTLY used? → LRU (one DLL + map).   │\n"
        "│                     │ Evict LEAST FREQUENTLY used? → LFU (two maps + freq │\n"
        "│                     │ buckets — significantly more complex).              │\n"
        "├─────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Plain hash map      │ Bounded capacity with eviction? → LRU Cache.        │\n"
        "│                     │ Just O(1) lookup, no eviction? → dict.              │\n"
        "└─────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• Can you implement LFU Cache in O(1)?\n"
        "• Why do you need a doubly linked list? Would singly linked work?\n"
        "• What changes if you need a thread-safe LRU cache?"
    ),
    "time": "O(1) get and put",
    "space": "O(capacity)",
    "problems": [
        ("LRU Cache", "M"),
        ("LFU Cache", "H"),
        ("Design Twitter", "M"),
        ("Design In-Memory File Sys", "H"),
        ("All O(1) Data Structure", "H"),
    ],
    "related": ["Linked List", "Arrays & Hashing", "Queue"],
}
