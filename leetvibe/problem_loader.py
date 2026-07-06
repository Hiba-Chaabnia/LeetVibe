"""
Problem loader for LeetVibe.
Reads problem JSON files from the problems/ directory.

Handles two on-disk formats transparently:
  Formatted (created by expand_problems.py):
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


PROBLEMS_DIR = Path(__file__).parent / "data" / "problems"

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}
DIFFICULTY_COLORS = {
    "easy": "green",
    "medium": "yellow",
    "hard": "red",
}

_HTML_TAG = re.compile(r"<[^>]+>")
_HTML_ENTITIES_RE = re.compile(r"&(?:nbsp|lt|gt|amp|quot|#39);")
_HTML_ENTITY_MAP = {
    "&nbsp;": " ", "&lt;": "<", "&gt;": ">",
    "&amp;": "&", "&quot;": '"', "&#39;": "'",
}
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def _strip_html(text: str) -> str:
    text = _HTML_TAG.sub("", text)
    text = _HTML_ENTITIES_RE.sub(lambda m: _HTML_ENTITY_MAP[m.group()], text)
    return _MULTI_NEWLINE_RE.sub("\n\n", text).strip()


@dataclass
class Problem:
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
    def from_file(cls, path: Path) -> "Problem":
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


def session_slug(problem: Problem) -> str:
    """Identifier for *problem* inside AI chat-session Firestore doc ids.

    Historically falls back to the display title — Problem has no
    title_slug field, so that branch never actually fires — but is kept
    exactly as-is (not switched to problem.id, a *different* slug used by
    mark_solved/get_solved_slugs) so existing users' chat_sessions /
    chat_messages doc ids don't shift under them. Shared by every caller
    that needs to reference an AI session's doc id, so they can't drift
    from each other the way two separate inline copies eventually would.
    """
    return getattr(problem, "title_slug", None) or problem.title


_problems_cache: list[Problem] | None = None


def load_all_problems() -> list[Problem]:
    """Load every problem JSON from the problems/ tree, sorted by difficulty then title.

    Result is cached in memory so repeated calls (e.g. from load_by_difficulty,
    load_by_id) do not re-parse the 3,000+ JSON files each time.
    """
    global _problems_cache
    if _problems_cache is not None:
        return _problems_cache

    problems: list[Problem] = []
    seen_ids: set[str] = set()
    if not PROBLEMS_DIR.exists():
        return problems

    for json_file in PROBLEMS_DIR.rglob("*.json"):
        try:
            ch = Problem.from_file(json_file)
            if ch.id not in seen_ids:
                seen_ids.add(ch.id)
                problems.append(ch)
        except (json.JSONDecodeError, KeyError):
            continue  # skip malformed files

    problems.sort(key=lambda c: (DIFFICULTY_ORDER.get(c.difficulty, 99), c.title))
    _problems_cache = problems
    return problems


def load_by_difficulty(difficulty: str) -> list[Problem]:
    return [c for c in load_all_problems() if c.difficulty == difficulty.lower()]


def load_by_id(problem_id: str) -> Optional[Problem]:
    for problem in load_all_problems():
        if problem.id == problem_id:
            return problem
    return None


def get_random_problem(difficulty: Optional[str] = None) -> Optional[Problem]:
    import random
    pool = load_by_difficulty(difficulty) if difficulty else load_all_problems()
    return random.choice(pool) if pool else None
