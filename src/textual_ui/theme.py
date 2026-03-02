"""LeetVibe TUI color palette — single source of truth for brand colors."""

# ── Difficulty / status ───────────────────────────────────────────────────────
GREEN = "#00C44F"   # easy difficulty / success / signed-in
BLUE  = "#4A9EFF"   # submit / info
RED   = "#E53935"   # hard difficulty / error
AMBER = "#FFB300"   # medium difficulty / warning
DIM   = "#888888"   # muted text / secondary labels

# ── Brand gradient — warm gold → deep lava ────────────────────────────────────
GOLD  = "#FFD700"   # bright golden yellow  (gradient step 1)
HONEY = "#FFAF00"   # warm amber-honey      (gradient step 2)
FIRE  = "#FF8205"   # primary brand orange  (gradient step 3)
EMBER = "#FA500F"   # deep orange-red       (gradient step 4)
LAVA  = "#E92700"   # intense red-orange    (gradient step 5)

GRADIENT: list[str] = [GOLD, HONEY, FIRE, EMBER, LAVA]
