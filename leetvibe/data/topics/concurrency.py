from __future__ import annotations

TOPIC: dict = {
    "title": "Concurrency",
    "slug": "Concurrency",
    "recognize": (
        "\"print in order\", \"print FooBar alternately\", \"dining philosophers\",\n"
        "  \"H2O\", \"web crawler multithreaded\", synchronisation between threads."
    ),
    "diagram": (
        "  Python synchronisation primitives:\n"
        "\n"
        "  threading.Lock()        — mutual exclusion (only one thread at a time)\n"
        "  threading.Semaphore(n)  — allow up to n threads at a time\n"
        "                            sem.acquire() blocks when count = 0\n"
        "                            sem.release() increments count\n"
        "  threading.Event()       — one thread signals, another waits\n"
        "                            event.wait() blocks until event.set()\n"
        "  threading.Barrier(n)    — all n threads must reach barrier before any continue\n"
        "  threading.Condition()   — lock + wait/notify for complex coordination\n"
        "\n"
        "  Pattern: Semaphore(0) as a gate\n"
        "  Thread A: do work, then sem.release()   # open the gate\n"
        "  Thread B: sem.acquire(), then do work   # wait at gate"
    ),
    "when": (
        "LeetCode Concurrency problems (tag: concurrency).\n"
        "  Synchronise multiple threads with ordering or mutual-exclusion constraints."
    ),
    "pattern": (
        "import threading\n"
        "\n"
        "# Print in Order — A before B before C\n"
        "class Foo:\n"
        "    def __init__(self):\n"
        "        self.sem_b = threading.Semaphore(0)  # B waits here\n"
        "        self.sem_c = threading.Semaphore(0)  # C waits here\n"
        "\n"
        "    def first(self, printFirst):\n"
        "        printFirst()\n"
        "        self.sem_b.release()    # unlock B\n"
        "\n"
        "    def second(self, printSecond):\n"
        "        self.sem_b.acquire()    # wait for A\n"
        "        printSecond()\n"
        "        self.sem_c.release()    # unlock C\n"
        "\n"
        "    def third(self, printThird):\n"
        "        self.sem_c.acquire()    # wait for B\n"
        "        printThird()"
    ),
    "pattern2": (
        "# Print FooBar Alternately\n"
        "import threading\n"
        "\n"
        "class FooBar:\n"
        "    def __init__(self, n):\n"
        "        self.n = n\n"
        "        self.foo_sem = threading.Semaphore(1)  # foo goes first\n"
        "        self.bar_sem = threading.Semaphore(0)  # bar waits\n"
        "\n"
        "    def foo(self, printFoo):\n"
        "        for _ in range(self.n):\n"
        "            self.foo_sem.acquire()\n"
        "            printFoo()\n"
        "            self.bar_sem.release()\n"
        "\n"
        "    def bar(self, printBar):\n"
        "        for _ in range(self.n):\n"
        "            self.bar_sem.acquire()\n"
        "            printBar()\n"
        "            self.foo_sem.release()\n"
        "\n"
        "# H2O — 2 hydrogen threads + 1 oxygen thread per molecule\n"
        "class H2O:\n"
        "    def __init__(self):\n"
        "        self.h_sem = threading.Semaphore(2)  # 2 H allowed\n"
        "        self.o_sem = threading.Semaphore(0)  # O waits for 2 H\n"
        "        self.barrier = threading.Barrier(3)  # sync all 3 before next\n"
        "\n"
        "    def hydrogen(self, releaseHydrogen):\n"
        "        self.h_sem.acquire()\n"
        "        releaseHydrogen()\n"
        "        self.barrier.wait()    # wait for both H + O\n"
        "        self.o_sem.release()   # signal O\n"
        "\n"
        "    def oxygen(self, releaseOxygen):\n"
        "        self.o_sem.acquire()   # wait for 2 H\n"
        "        releaseOxygen()\n"
        "        self.barrier.wait()    # sync\n"
        "        self.h_sem.release()   # release 2 H for next molecule\n"
        "        self.h_sem.release()"
    ),
    "pitfalls": (
        "• Semaphore(0) starts locked — the first acquire() blocks immediately.\n"
        "  Semaphore(1) starts open — first acquire() passes through.\n"
        "• Always acquire before the work and release after — swapping order\n"
        "  creates race conditions or deadlocks.\n"
        "• threading.Lock() is not reentrant — a thread that holds the lock\n"
        "  and tries to acquire it again will deadlock. Use RLock() if needed.\n"
        "• Python's GIL limits true parallelism for CPU-bound tasks;\n"
        "  these problems test synchronisation logic, not speed."
    ),
    "time": "O(n)  per thread  (synchronisation overhead is O(1) per primitive)",
    "space": "O(1)  semaphores / locks",
    "problems": [
        ("Print in Order",          "E"),
        ("Print FooBar Alternately","M"),
        ("Print Zero Even Odd",     "M"),
        ("Building H2O",            "M"),
        ("The Dining Philosophers", "M"),
        ("Web Crawler Multithreaded","M"),
    ],
    "related": ["Queue", "Iterator Design Pattern"],
}
