from __future__ import annotations

import importlib
from pathlib import Path

from ._selector import TOPIC as _selector_topic
from ._metadata import TOPIC_META, CATEGORIES, TIER_MAP

# Pattern Selector nav entry always comes first; remaining topics auto-discovered
# alphabetically from all non-underscore .py files in this directory.
TOPICS: list[dict] = [_selector_topic]

for _f in sorted(Path(__file__).parent.glob("*.py")):
    if not _f.stem.startswith("_"):
        _mod = importlib.import_module(f".{_f.stem}", package=__name__)
        TOPICS.append(_mod.TOPIC)

# Enrich every topic dict with category / tier / parent from metadata
for _t in TOPICS:
    _m = TOPIC_META.get(_t["title"], {"category": "Misc Patterns", "tier": 2, "parent": ""})
    _t["category"] = _m["category"]
    _t["tier"]     = _m["tier"]
    _t["parent"]   = _m["parent"]

__all__ = ["TOPICS", "CATEGORIES", "TIER_MAP", "TOPIC_META"]
