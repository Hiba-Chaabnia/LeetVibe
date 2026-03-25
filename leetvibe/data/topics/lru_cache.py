from __future__ import annotations

TOPIC: dict = {
    "title": "LRU Cache",
    "slug": "LRU Cache",
    "recognize": (
        "LRU cache, most recently used, evict least recently used,\n"
        "O(1) get and put with bounded capacity, LFU cache."
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
    "when": (
        "Any fixed-capacity cache requiring O(1) lookup AND O(1) eviction\n"
        "of the least recently used item."
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
                "    def _insert_tail(self, node):          # insert just before tail\n"
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
                "            lru = self.head.next           # evict LRU\n"
                "            self._remove(lru)\n"
                "            del self.cache[lru.key]"
            ),
        },
        {
            "name": "Python shortcut: OrderedDict maintains insertion order",
            "code": (
                "# move_to_end() + popitem(last=False) implement LRU in ~10 lines\n"
                "from collections import OrderedDict\n"
                "\n"
                "class LRUCache:\n"
                "    def __init__(self, capacity):\n"
                "        self.cap   = capacity\n"
                "        self.cache = OrderedDict()\n"
                "\n"
                "    def get(self, key):\n"
                "        if key not in self.cache: return -1\n"
                "        self.cache.move_to_end(key)    # mark as most recently used\n"
                "        return self.cache[key]\n"
                "\n"
                "    def put(self, key, value):\n"
                "        if key in self.cache:\n"
                "            self.cache.move_to_end(key)\n"
                "        self.cache[key] = value\n"
                "        if len(self.cache) > self.cap:\n"
                "            self.cache.popitem(last=False)  # evict LRU (first item)"
            ),
        },
    ],
    "pitfalls": (
        "• Always update both the hash map AND the linked list together —\n"
        "  forgetting to del cache[lru.key] after eviction causes memory leak.\n"
        "• Dummy head/tail sentinels eliminate all edge-case checks for empty list.\n"
        "• Python's OrderedDict is interview-acceptable but interviewers often\n"
        "  expect the doubly linked list implementation to test pointer manipulation.\n"
        "• LFU cache (evict least frequently used) needs TWO hash maps + freq tracking."
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
