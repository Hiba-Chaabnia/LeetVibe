"""Playbook rendering — topic → Rich markup, plus notes/history persistence."""

from __future__ import annotations

import json
import re
from pathlib import Path

from leetvibe.ui.markup import (
    code_block as _code_block,
    esc,
    md_inline as _md_inline,
    render_response_to_markup,
)
from leetvibe.ui.theme import AMBER, DIM, GRADIENT, GREEN, RED

# ── Notes persistence ──────────────────────────────────────────────────────────

_NOTES_DIR  = Path.home() / ".leetvibe"
_NOTES_FILE = _NOTES_DIR / "notes.json"


def load_notes() -> dict[str, str]:
    try:
        return json.loads(_NOTES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_notes(notes: dict[str, str]) -> None:
    try:
        _NOTES_DIR.mkdir(parents=True, exist_ok=True)
        _NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


_HISTORIES_FILE = _NOTES_DIR / "chat_histories.json"


def load_histories() -> dict[str, list[dict]]:
    try:
        return json.loads(_HISTORIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_histories(histories: dict[str, list[dict]]) -> None:
    try:
        _NOTES_DIR.mkdir(parents=True, exist_ok=True)
        _HISTORIES_FILE.write_text(
            json.dumps(histories, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


# ── Rich markup helper ─────────────────────────────────────────────────────────

# ── Difficulty badge helpers ───────────────────────────────────────────────────

_DIFF_COLOR = {"E": GREEN, "M": AMBER, "H": RED}
_DIFF_LABEL = {"E": "Easy", "M": "Med ", "H": "Hard"}


# ── Content renderer ───────────────────────────────────────────────────────────

def _sh(label: str, idx: int = 0) -> str:
    """Section header: title-case label in a cycling gradient color."""
    color = GRADIENT[idx % len(GRADIENT)]
    return f"[bold {color}]{label.title()}[/bold {color}]"


_SENTENCE_END = (".", "?", "!")


def _wrap_prose(text: str) -> list[str]:
    """Collapse hand-wrapped continuation lines into one logical line per bullet.

    Topic content authors hard-wrap long bullets/sentences across physical
    lines in the source file (sometimes with a leading-space continuation,
    sometimes not — there's no consistent marker). Static already word-wraps
    at render time, so re-emitting each physical line separately double-wraps
    content once the panel is narrower than the author's assumed width (e.g.
    with the chat panel open), producing stray mid-sentence indents.

    A physical line continues the previous one unless that previous line
    already ended a sentence (`.`, `?`, `!`) — mid-sentence breaks end in a
    comma, semicolon, dash, or nothing at all. Merging continuations back
    into one logical line lets Static's own wrap be the only thing deciding
    where lines break, regardless of panel width.
    """
    merged: list[str] = []
    for raw in text.split("\n"):
        stripped = raw.strip()
        if merged and not merged[-1].endswith(_SENTENCE_END):
            merged[-1] = f"{merged[-1]} {stripped}"
        else:
            merged.append(stripped)
    return merged


def render_title(title: str) -> str:
    """Title with fire gradient per character."""
    title = title.upper()
    n = len(title)
    chars = []
    for i, ch in enumerate(title):
        idx = min(int(i / max(n - 1, 1) * (len(GRADIENT) - 1) + 0.5), len(GRADIENT) - 1)
        color = GRADIENT[idx]
        chars.append(f"[bold {color}]{ch}[/bold {color}]")
    return "".join(chars)


# esc / _md_inline / _code_block / render_response_to_markup live in
# leetvibe.ui.markup (shared with the agent session's bubble log); imported
# above so playbook callers keep their historical import path.


def build_topic_context(topic: dict) -> str:
    """Build a concise reference string for the AI system prompt."""
    parts = [f"Pattern: {topic['title']}"]
    if topic.get("recognize"):
        parts.append(f"Recognised by: {topic['recognize']}")
    if topic.get("intuition"):
        parts.append(f"Intuition: {topic['intuition']}")
    if topic.get("time") or topic.get("space"):
        parts.append(
            f"Complexity: Time {topic.get('time', '?')}, Space {topic.get('space', '?')}"
        )
    if topic.get("patterns"):
        parts.append("Code patterns:")
        for pat in topic["patterns"]:
            parts.append(f"  {pat['name']}:")
            parts.append(f"```python\n{pat['code']}\n```")
    if topic.get("variants"):
        parts.append(f"Variants: {topic['variants']}")
    if topic.get("pitfalls"):
        parts.append(f"Pitfalls: {topic['pitfalls']}")
    return "\n".join(parts)


def render_topic(topic: dict, note: str) -> str:
    """Build a Rich-markup string for the right panel."""

    # ── Pattern Selector (special layout) ───────────────────────────────
    if topic["slug"] == "_selector":
        lines: list[str] = [
            "",
            _sh("How to pick a pattern", 0),
        ]
        for ln in esc(topic["diagram"]).split("\n"):
            lines.append(f"  {ln}")
        lines += [
            f"  [{DIM}]{'─' * 48}[/{DIM}]",
            "",
            f"  [{DIM}]{esc(topic.get('when', ''))}[/{DIM}]",
        ]
        return "\n".join(lines)

    diagram   = esc(topic.get("diagram", ""))
    t_val     = esc(topic.get("time", ""))
    s_val     = esc(topic.get("space", ""))
    confusion = esc(topic.get("confusion", ""))
    # Prose fields are NOT pre-escaped: _md_inline escapes brackets itself,
    # and escaping twice renders literal backslashes (nums\[i]).
    recognize = topic.get("recognize", "")
    intuition = topic.get("intuition", "")
    pitfalls  = topic.get("pitfalls", "")
    edge_cases = topic.get("edge_cases", "")
    variants  = topic.get("variants", "")
    follow_up = topic.get("follow_up_questions", "")
    related   = topic.get("related", [])

    lines: list[str] = [""]
    h = 0  # gradient index for section headers

    # Recognised by
    if recognize:
        lines.append(_sh("Recognised by", h)); h += 1
        for ln in _wrap_prose(recognize):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Intuition
    if intuition:
        lines.append(_sh("Intuition", h)); h += 1
        for ln in _wrap_prose(intuition):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Diagram
    lines.append(_sh("Diagram", h)); h += 1
    for ln in diagram.split("\n"):
        lines.append(f"  {ln}")
    lines.append("")

    # Patterns
    patterns = topic.get("patterns", [])
    if patterns:
        lines.append(_sh("Patterns", h)); h += 1
        for i, pat in enumerate(patterns, 1):
            lines.append(f"  [bold #ffffff]{i}. {esc(pat['name'])}[/bold #ffffff]")
            # _code_block escapes internally — passing esc'ed code doubles it
            lines += _code_block(pat["code"], width=48)
            lines.append("")

    # Variants
    if variants:
        lines.append(_sh("Variants", h)); h += 1
        for ln in _wrap_prose(variants):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Complexity
    if t_val or s_val:
        lines.append(_sh("Complexity", h)); h += 1
        if t_val:
            lines.append(f"  Time   {t_val}")
        if s_val:
            lines.append(f"  Space  {s_val}")
        lines.append("")

    # Pitfalls
    if pitfalls:
        lines.append(_sh("Pitfalls", h)); h += 1
        for ln in _wrap_prose(pitfalls):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Edge cases
    if edge_cases:
        lines.append(_sh("Edge cases", h)); h += 1
        for ln in _wrap_prose(edge_cases):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Don't mix up with
    if confusion:
        lines.append(_sh("Don't mix up with", h)); h += 1
        for ln in confusion.split("\n"):
            lines.append(f"  {ln}")
        lines.append("")

    # Follow-up questions
    if follow_up:
        lines.append(_sh("Follow-up questions", h)); h += 1
        for ln in _wrap_prose(follow_up):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Classic Problems
    if topic.get("problems"):
        lines.append(_sh("Classic Problems", h)); h += 1
        for item in topic["problems"]:
            if isinstance(item, tuple):
                name, diff = item
                dc = _DIFF_COLOR.get(diff, DIM)
                dl = _DIFF_LABEL.get(diff, diff)
                lines.append(
                    f"  [{DIM}]•[/{DIM}] {esc(name)}  [{dc}][{dl}][/{dc}]"
                )
            else:
                lines.append(f"  [{DIM}]•[/{DIM}] {esc(str(item))}")
        lines.append("")

    # Related Topics
    if related:
        lines.append(_sh("Related Topics", h)); h += 1
        lines.append("  " + "  ·  ".join(esc(r) for r in related))
        lines.append("")

    # Notes
    if note.strip():
        lines.append(_sh("My Notes", h))
        for note_line in note.strip().split("\n"):
            lines.append(f"  {esc(note_line)}")
    else:
        lines.append(
            f"  [{DIM}]No notes yet — press [bold]Ctrl+N[/bold] to add one.[/{DIM}]"
        )

    return "\n".join(lines)
