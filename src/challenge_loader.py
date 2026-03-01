"""
Challenge loader for LeetVibe.
Reads problem JSON files from the challenges/ directory.

Handles two on-disk formats transparently:
  Formatted (created by expand_challenges.py):
    { "id", "title", "difficulty" (lowercase), "description", "python_solution",
      "hints", "topics", "test_cases" }
  Raw HuggingFace (greengerong/leetcode dataset):
    { "questionId", "titleSlug", "title", "difficulty" (Title-case), "content" (HTML),
      "topicTags": [{"name": ...}], "hints": [...], "python", ... }
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


CHALLENGES_DIR = Path(__file__).parent.parent / "problems"

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2, "trading": 3}
DIFFICULTY_COLORS = {
    "easy": "green",
    "medium": "yellow",
    "hard": "red",
    "trading": "cyan",
}

_HTML_TAG = re.compile(r"<[^>]+>")
_HTML_ENTITIES = [
    ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"),
    ("&amp;", "&"), ("&quot;", '"'), ("&#39;", "'"),
]


def _strip_html(text: str) -> str:
    text = _HTML_TAG.sub("", text)
    for entity, replacement in _HTML_ENTITIES:
        text = text.replace(entity, replacement)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


@dataclass
class Challenge:
    id: str
    title: str
    difficulty: str
    description: str
    hints: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    python_solution: str = ""
    python_snippet: str = ""
    solution_explanation: str = ""
    test_cases: list[list[str]] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)
    has_solutions: bool = False

    @classmethod
    def from_file(cls, path: Path) -> "Challenge":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # --- ID: prefer explicit "id", then "titleSlug", then filename stem ---
        cid = data.get("id") or data.get("titleSlug") or path.stem

        # --- Title: strip accidental leading/trailing whitespace ---
        title = (data.get("title") or path.stem.replace("-", " ").title()).strip()

        # --- Difficulty: normalise to lowercase; fall back to folder name ---
        raw_diff = data.get("difficulty", "") or ""
        difficulty = raw_diff.lower() or path.parent.name

        # --- Description: prefer clean "description", fall back to HTML "content" ---
        description = data.get("description") or _strip_html(data.get("content") or "")

        # --- Hints: may be a list of strings or a list of dicts {"hint": "..."} ---
        raw_hints = data.get("hints") or []
        hints: list[str] = []
        for h in raw_hints:
            if isinstance(h, str):
                hints.append(h)
            elif isinstance(h, dict):
                hints.append(h.get("hint") or h.get("text") or str(h))

        # --- Topics: prefer "topics" list; fall back to "topicTags" [{name: ...}] ---
        raw_topics = data.get("topics")
        if raw_topics:
            topics = [str(t) for t in raw_topics if t]
        else:
            topics = [
                t["name"] for t in (data.get("topicTags") or [])
                if isinstance(t, dict) and t.get("name")
            ]

        # --- Solutions block (raw HuggingFace format) ---
        solutions = data.get("solutions") or {}
        python_solution = (
            data.get("python_solution")
            or solutions.get("python")
            or data.get("python")
            or ""
        )
        solution_explanation = solutions.get("explanation") or ""

        # --- Code snippets (starter templates — Python only) ---
        python_snippet = ""
        for snippet in data.get("codeSnippets") or []:
            slug = (snippet.get("langSlug") or "").lower()
            code = snippet.get("code") or ""
            if slug == "python" and not python_snippet:
                python_snippet = code

        # --- Test cases: structured list[list[str]], expected outputs: list[str] ---
        test_cases = data.get("testCases") or []
        expected_outputs = data.get("expectedOutputs") or []

        return cls(
            id=cid,
            title=title,
            difficulty=difficulty,
            description=description,
            hints=hints,
            topics=topics,
            python_solution=python_solution,
            python_snippet=python_snippet,
            solution_explanation=solution_explanation,
            test_cases=test_cases,
            expected_outputs=expected_outputs,
            has_solutions=bool(data.get("has_solutions", False)),
        )

    @property
    def difficulty_color(self) -> str:
        return DIFFICULTY_COLORS.get(self.difficulty, "white")

    @property
    def hint_count(self) -> int:
        return len(self.hints)


def load_all_challenges() -> list[Challenge]:
    """Load every challenge JSON from the challenges/ tree, sorted by difficulty then title."""
    challenges: list[Challenge] = []
    seen_ids: set[str] = set()
    if not CHALLENGES_DIR.exists():
        return challenges

    for json_file in CHALLENGES_DIR.rglob("*.json"):
        try:
            ch = Challenge.from_file(json_file)
            if ch.id not in seen_ids:
                seen_ids.add(ch.id)
                challenges.append(ch)
        except (json.JSONDecodeError, KeyError):
            continue  # skip malformed files

    challenges.sort(key=lambda c: (DIFFICULTY_ORDER.get(c.difficulty, 99), c.title))
    return challenges


def load_by_difficulty(difficulty: str) -> list[Challenge]:
    return [c for c in load_all_challenges() if c.difficulty == difficulty.lower()]


def load_by_id(challenge_id: str) -> Optional[Challenge]:
    for challenge in load_all_challenges():
        if challenge.id == challenge_id:
            return challenge
    return None


def get_random_challenge(difficulty: Optional[str] = None) -> Optional[Challenge]:
    import random
    pool = load_by_difficulty(difficulty) if difficulty else load_all_challenges()
    return random.choice(pool) if pool else None
