from __future__ import annotations

TOPIC: dict = {
    "title": "Concurrency",
    "slug": "Concurrency",
    "recognize": (
        "Print in order, print FooBar alternately, dining philosophers, H2O, web crawler multithreaded.\n"
        "Keywords: synchronise multiple threads, ordering constraint, mutual exclusion, LeetCode 'Concurrency' tag."
    ),
    "intuition": (
        "• A semaphore is a blocking counter — Semaphore(0) forces the acquirer to wait until another\n"
        "  thread calls release(), which is exactly how you encode 'B must run after A'.\n"
        "• Threads aren't actually racing for speed here — you're constraining WHEN each is allowed\n"
        "  to proceed, not computing anything faster than a single thread would.\n"
        "• Lock = mutual exclusion (one at a time). Semaphore(n) = bounded concurrency (up to n at a time).\n"
        "  Pick the primitive whose shape matches the constraint."
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
    "patterns": [
        {
            "name": "Print in Order — A before B before C",
            "code": (
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
        },
        {
            "name": "Print FooBar Alternately",
            "code": (
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
                "        self.h_sem = threading.Semaphore(2)  # at most 2 H per molecule\n"
                "        self.o_sem = threading.Semaphore(1)  # at most 1 O per molecule\n"
                "        self.barrier = threading.Barrier(3)  # gather 2 H + 1 O\n"
                "\n"
                "    def hydrogen(self, releaseHydrogen):\n"
                "        self.h_sem.acquire()   # claim an H slot\n"
                "        self.barrier.wait()    # wait until 2 H + 1 O gathered\n"
                "        releaseHydrogen()\n"
                "        self.h_sem.release()   # free the slot for the next molecule\n"
                "\n"
                "    def oxygen(self, releaseOxygen):\n"
                "        self.o_sem.acquire()   # claim the O slot\n"
                "        self.barrier.wait()    # wait until 2 H + 1 O gathered\n"
                "        releaseOxygen()\n"
                "        self.o_sem.release()   # free the slot for the next molecule"
            ),
        },
    ],
    "variants": (
        "• Strict order (A→B→C) — chain of semaphores; each stage releases the next in line.\n"
        "• Alternating execution (FooBar) — two semaphores ping-pong; one pre-acquired to go first.\n"
        "• N-of-M rendezvous (H2O) — Semaphore(k) caps concurrent entrants + Barrier(k) syncs completion.\n"
        "• Producer/consumer hand-off — queue.Queue (already thread-safe) instead of manual semaphores.\n"
        "• Reader/writer coordination — multiple concurrent readers, one exclusive writer (Condition)."
    ),
    "pitfalls": (
        "• Semaphore(0) starts locked — first acquire() blocks immediately.\n"
        "  Semaphore(1) starts open — first acquire() passes through.\n"
        "• Acquire before the work, release after — swapping the order causes races or deadlocks.\n"
        "• threading.Lock() is not reentrant — a thread re-acquiring its own lock deadlocks; use RLock().\n"
        "• Python's GIL limits true CPU parallelism — these problems test synchronisation logic, not speed."
    ),
    "edge_cases": (
        "• n=0 (e.g. FooBar with zero iterations) — loop body never runs; no acquire/release fires.\n"
        "• Single thread only — semaphores still work, just add pure overhead; no deadlock risk.\n"
        "• Reentrant acquire by the same thread on a plain Lock — deadlocks immediately; needs RLock.\n"
        "• More threads than Semaphore(k)'s cap — extra threads block until a release happens."
    ),
    "confusion": (
        "┌───────────────────────────┬─────────────────────────────────────────────────────┐\n"
        "│ Often confused with       │ Distinguishing question                             │\n"
        "├───────────────────────────┼─────────────────────────────────────────────────────┤\n"
        "│ Queue (producer/consumer) │ Just need thread-safe FIFO hand-off? → queue.Queue. │\n"
        "│                           │ Need custom ordering/gating logic? → semaphores.    │\n"
        "└───────────────────────────┴─────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What happens if you swap the acquire/release order in one thread?\n"
        "• How would you generalise Print in Order to N functions instead of 3?\n"
        "• Why doesn't Python's GIL make these synchronisation problems unnecessary?\n"
        "• How would you implement this with a Condition variable instead of semaphores?"
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
