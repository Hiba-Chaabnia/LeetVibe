from __future__ import annotations

TOPIC: dict = {
    "title": "Math Patterns",
    "slug": "Math",
    "recognize": (
        "prime, GCD, LCM, power, modulo, factorial,\n"
        "digit, base conversion, count primes, happy number."
    ),
    "diagram": (
        "  GCD (Euclidean):  gcd(a,b) = gcd(b, a%b)  until b=0\n"
        "  gcd(48,18) → gcd(18,12) → gcd(12,6) → gcd(6,0) = 6\n"
        "\n"
        "  Fast Power (binary exponentiation):\n"
        "  2^13 = 2^8 × 2^4 × 2^1   (13 = 1101 in binary)\n"
        "  O(log n) multiplications\n"
        "\n"
        "  Sieve of Eratosthenes  O(n log log n):\n"
        "  mark every multiple of p (p*p, p*p+p, ...) as composite"
    ),
    "when": (
        "Number theory problems: primes, GCD, modular arithmetic,\n"
        "combinatorics (nCr mod p), or digit manipulation."
    ),
    "patterns": [
        {
            "name": "Fast power  O(log exp)",
            "code": (
                "from math import gcd\n"
                "\n"
                "# Fast power  O(log exp)\n"
                "def fast_pow(base, exp, mod):\n"
                "    result = 1\n"
                "    base %= mod\n"
                "    while exp > 0:\n"
                "        if exp & 1:\n"
                "            result = result * base % mod\n"
                "        base = base * base % mod\n"
                "        exp >>= 1\n"
                "    return result\n"
                "# or simply: pow(base, exp, mod)  — Python built-in\n"
                "\n"
                "# Sieve of Eratosthenes\n"
                "def count_primes(n):\n"
                "    sieve = [True] * n\n"
                "    sieve[0] = sieve[1] = False\n"
                "    for p in range(2, int(n**0.5) + 1):\n"
                "        if sieve[p]:\n"
                "            for m in range(p * p, n, p):\n"
                "                sieve[m] = False\n"
                "    return sum(sieve)"
            ),
        },
        {
            "name": "Happy Number — cycle detection via fast/slow pointers",
            "code": (
                "def digit_square_sum(n):\n"
                "    s = 0\n"
                "    while n:\n"
                "        n, d = divmod(n, 10)\n"
                "        s += d * d\n"
                "    return s\n"
                "\n"
                "slow = fast = n\n"
                "while True:\n"
                "    slow = digit_square_sum(slow)\n"
                "    fast = digit_square_sum(digit_square_sum(fast))\n"
                "    if slow == fast:\n"
                "        return slow == 1\n"
                "\n"
                "# ── Modular Arithmetic ───────────────────────────────────────────\n"
                "MOD = 10 ** 9 + 7\n"
                "\n"
                "# Modular inverse via Fermat's little theorem (MOD must be prime)\n"
                "# inv(a) = a^(MOD-2) mod MOD\n"
                "def mod_inv(a, mod=MOD):\n"
                "    return pow(a, mod - 2, mod)   # Python built-in handles this fast\n"
                "\n"
                "# nCr mod p — precompute factorials and inverse factorials\n"
                "def precompute(n, mod=MOD):\n"
                "    fact    = [1] * (n + 1)\n"
                "    inv_fact = [1] * (n + 1)\n"
                "    for i in range(1, n + 1):\n"
                "        fact[i] = fact[i - 1] * i % mod\n"
                "    inv_fact[n] = pow(fact[n], mod - 2, mod)\n"
                "    for i in range(n - 1, -1, -1):\n"
                "        inv_fact[i] = inv_fact[i + 1] * (i + 1) % mod\n"
                "    return fact, inv_fact\n"
                "\n"
                "def ncr(n, r, fact, inv_fact, mod=MOD):\n"
                "    if r < 0 or r > n: return 0\n"
                "    return fact[n] * inv_fact[r] % mod * inv_fact[n - r] % mod\n"
                "# Quick one-off: math.comb(n, r) % MOD  (fine for small n)"
            ),
        },
    ],
    "pitfalls": (
        "• Apply mod after every multiplication: result = result * base % mod.\n"
        "• Sieve: start marking from p*p (not 2*p) — smaller multiples already marked.\n"
        "• Use Python's built-in pow(base, exp, mod) — it is an optimised fast power.\n"
        "• Modular inverse only works when MOD is prime (Fermat's little theorem).\n"
        "• nCr: precompute factorials once, then answer each query in O(1)."
    ),
    "time": "O(log n) GCD / fast-pow   /   O(n log log n) sieve   /   O(n) nCr precompute",
    "space": "O(1) math ops   /   O(n) sieve / nCr table",
    "problems": [
        ("Count Primes",             "M"),
        ("Happy Number",             "E"),
        ("Pow(x, n)",                "M"),
        ("Reverse Integer",          "M"),
        ("Excel Sheet Column Title", "E"),
        ("Sqrt(x)",                  "E"),
        ("Unique Paths",             "M"),
        ("Pascal's Triangle",        "E"),
    ],
    "related": ["Bit Manipulation", "Dynamic Programming", "Digit DP", "Probability DP", "Game Theory"],
}
