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

# Smooth 24-step ping-pong gradient used for shimmer animations (gold → lava → gold)
SHIMMER: list[str] = [
    "#FFD700", "#FFCB00", "#FFC000", "#FFB500", "#FFAF00",
    "#FFA000", "#FF9000", "#FF8205", "#FF6E05", "#FA500F",
    "#F63C12", "#F02B15", "#E92700",
    "#F02B15", "#F63C12", "#FA500F", "#FF6E05", "#FF8205",
    "#FF9000", "#FFA000", "#FFAF00", "#FFB500", "#FFC000",
    "#FFCB00",
]
