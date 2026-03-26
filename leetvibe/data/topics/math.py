from __future__ import annotations

TOPIC: dict = {
    "title": "Math Patterns",
    "slug": "Math",
    "recognize": (
        "Prime, GCD, LCM, power, modulo, factorial, digit, base conversion, count primes, happy number.\n"
        "Keywords: nCr mod p, modular inverse, fast exponentiation, sieve."
    ),
    "intuition": (
        "• Binary exponentiation: decompose exp in binary — only set bits contribute; O(log n) multiplications.\n"
        "• GCD via Euclidean: gcd(a, b) = gcd(b, a%b) — the set of common divisors is preserved at each step.\n"
        "• Sieve of Eratosthenes: start marking from p² (not 2p) — all smaller multiples are already marked by earlier primes."
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
    "patterns": [
        {
            "name": "Fast power  O(log exp)",
            "code": (
                "from math import gcd\n"
                "\n"
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
            "name": "Modular arithmetic — nCr mod p",
            "code": (
                "MOD = 10 ** 9 + 7\n"
                "\n"
                "# Modular inverse via Fermat's little theorem (MOD must be prime)\n"
                "def mod_inv(a, mod=MOD):\n"
                "    return pow(a, mod - 2, mod)\n"
                "\n"
                "# nCr mod p — precompute factorials and inverse factorials once\n"
                "def precompute(n, mod=MOD):\n"
                "    fact     = [1] * (n + 1)\n"
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
                "\n"
                "# Happy Number — cycle detection via fast/slow pointers\n"
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
                "        return slow == 1"
            ),
        },
    ],
    "variants": (
        "• GCD — math.gcd(a, b); LCM = a * b // gcd(a, b).\n"
        "• Fast power — iterative binary exp; or pow(base, exp, mod) built-in.\n"
        "• Sieve of Eratosthenes — count/list primes up to n in O(n log log n).\n"
        "• Segmented sieve — primes in range [lo, hi] without a full sieve up to hi.\n"
        "• Modular inverse — Fermat's little theorem (mod must be prime) or extended Euclidean.\n"
        "• nCr mod p — precompute factorials + inverse factorials once; O(1) per query.\n"
        "• Digit manipulation — divmod(n, 10) extracts last digit; repeat until n=0.\n"
        "• Base conversion — repeated division by base; collect remainders in reverse."
    ),
    "pitfalls": (
        "• Apply mod after every multiplication: result = result * base % mod.\n"
        "• Sieve: start marking from p*p (not 2*p) — smaller multiples already marked.\n"
        "• Use Python's built-in pow(base, exp, mod) — it is an optimised fast power.\n"
        "• Modular inverse only works when MOD is prime (Fermat's little theorem).\n"
        "• nCr: precompute once, query in O(1) — don't call math.comb inside a loop."
    ),
    "edge_cases": (
        "• gcd(0, b) = b — math.gcd handles this; hand-rolled must guard against b=0 base case.\n"
        "• fast_pow(base, 0, mod) — loop doesn't execute; result = 1. Correct.\n"
        "• count_primes(0) or (1) — sieve[1] = False raises IndexError when n < 2; guard with 'if n < 2: return 0'.\n"
        "• mod_inv(0, mod) — 0 has no inverse; pow(0, mod-2, mod) = 0 (wrong); guard a=0."
    ),
    "confusion": (
        "┌─────────────────────┬──────────────────────────────────────────────────────┐\n"
        "│ Often confused with │ Distinguishing question                              │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ Bit manipulation    │ Binary representations for XOR/AND/OR logic? → Bits. │\n"
        "│                     │ Arithmetic with modulo or exponentiation? → Math.    │\n"
        "├─────────────────────┼──────────────────────────────────────────────────────┤\n"
        "│ DP counting         │ Combinatorial closed form (nCr, Catalan)? → Math.    │\n"
        "│                     │ State and transitions over sub-problems? → DP.       │\n"
        "└─────────────────────┴──────────────────────────────────────────────────────┘"
    ),
    "follow_up_questions": (
        "• What if MOD is not prime — can you still compute modular inverse?\n"
        "• Can you count primes faster than the sieve for very large n?\n"
        "• Why is pow(base, exp, mod) faster than base**exp % mod?"
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
