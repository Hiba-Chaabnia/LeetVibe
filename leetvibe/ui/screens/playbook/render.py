"""Playbook rendering — topic → Rich markup, plus notes/history persistence."""

from __future__ import annotations

import json
import re
from pathlib import Path

from leetvibe.ui.theme import AMBER, DIM, EMBER, GOLD, GRADIENT, GREEN, RED

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

def esc(text: str) -> str:
    """Escape [ so Rich doesn't interpret user content as markup tags."""
    return text.replace("[", r"\[")


# ── Difficulty badge helpers ───────────────────────────────────────────────────

_DIFF_COLOR = {"E": GREEN, "M": AMBER, "H": RED}
_DIFF_LABEL = {"E": "Easy", "M": "Med ", "H": "Hard"}


# ── Content renderer ───────────────────────────────────────────────────────────

def _sh(label: str, idx: int = 0) -> str:
    """Section header: title-case label in a cycling gradient color."""
    color = GRADIENT[idx % len(GRADIENT)]
    return f"[bold {color}]{label.title()}[/bold {color}]"


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


def _infobox(text: str) -> list[str]:
    """Render text in a softly dimmed infobox style."""
    return [f"  [{DIM}]{ln}[/{DIM}]" for ln in text.split("\n")]


def _code_block(block: str, width: int = 24) -> list[str]:
    """Render a code block with box-drawing header and │-prefixed lines."""
    # "  ┌── python " = 13 chars; fill rest with dashes up to total width
    dash_header = max(2, width - 13)
    dash_footer = max(2, width - 3)
    lines = [f"  [{DIM}]┌── python {'─' * dash_header}[/{DIM}]"]
    for ln in block.split("\n"):
        lines.append(f"  [{DIM}]│[/{DIM}] {ln}")
    lines.append(f"  [{DIM}]└{'─' * dash_footer}[/{DIM}]")
    return lines


def _md_inline(line: str) -> str:
    """Convert inline markdown to Rich markup, safely escaping literal brackets."""
    line = line.replace("[", "\x00")
    line = re.sub(r"\*\*(.+?)\*\*", r"[bold]\1[/bold]", line)
    line = re.sub(r"`([^`]+)`", rf"[bold {AMBER}]\1[/bold {AMBER}]", line)
    if re.match(r"^[-•]\s", line):
        line = f"  [{DIM}]•[/{DIM}] " + line[2:]
    line = line.replace("\x00", r"\[")
    return line


def render_response_to_markup(content: str) -> str:
    """Convert AI response markdown to a Rich markup string for Panel display."""
    lines_out: list[str] = []
    in_code = False
    code_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("```"):
            if in_code:
                for rendered in _code_block("\n".join(code_lines), width=22):
                    lines_out.append(rendered)
                lines_out.append("")
                code_lines = []
                in_code = False
            else:
                in_code = True
        elif in_code:
            code_lines.append(line)
        elif line.strip():
            lines_out.append(_md_inline(line))
        else:
            lines_out.append("")

    if in_code and code_lines:
        for rendered in _code_block("\n".join(code_lines), width=22):
            lines_out.append(rendered)

    while lines_out and not lines_out[-1].strip():
        lines_out.pop()

    return "\n".join(lines_out)


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
            f"  [{DIM}]{'─' * 48}[/{DIM}]",
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
    recognize = esc(topic.get("recognize", ""))
    intuition = esc(topic.get("intuition", ""))
    pitfalls  = esc(topic.get("pitfalls", ""))
    edge_cases = esc(topic.get("edge_cases", ""))
    variants  = esc(topic.get("variants", ""))
    confusion = esc(topic.get("confusion", ""))
    follow_up = esc(topic.get("follow_up_questions", ""))
    related   = topic.get("related", [])

    lines: list[str] = [""]
    h = 0  # gradient index for section headers

    # Recognised by
    if recognize:
        lines.append(_sh("Recognised by", h)); h += 1
        for ln in recognize.split("\n"):
            lines.append(f"  [{DIM}]{ln}[/{DIM}]")
        lines.append("")

    # Intuition
    if intuition:
        lines.append(_sh("Intuition", h)); h += 1
        for ln in intuition.split("\n"):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Diagram
    lines.append(_sh("Diagram", h)); h += 1
    lines += _infobox(diagram)
    lines.append("")

    # Patterns
    patterns = topic.get("patterns", [])
    if patterns:
        lines.append(_sh("Patterns", h)); h += 1
        for i, pat in enumerate(patterns, 1):
            lines.append(f"  [bold #ffffff]{i}. {esc(pat['name'])}[/bold #ffffff]")
            lines += _code_block(esc(pat["code"]), width=48)
            lines.append("")

    # Variants
    if variants:
        lines.append(_sh("Variants", h)); h += 1
        for ln in variants.split("\n"):
            lines.append(f"  {_md_inline(ln)}")
        lines.append("")

    # Complexity
    if t_val or s_val:
        lines.append(_sh("Complexity", h)); h += 1
        if t_val:
            lines.append(f"  Time   [{AMBER}]{t_val}[/{AMBER}]")
        if s_val:
            lines.append(f"  Space  [{AMBER}]{s_val}[/{AMBER}]")
        lines.append("")

    # Pitfalls
    if pitfalls:
        lines.append(_sh("Pitfalls", h)); h += 1
        for ln in pitfalls.split("\n"):
            lines.append(f"  [{RED}]{ln}[/{RED}]")
        lines.append("")

    # Edge cases
    if edge_cases:
        lines.append(_sh("Edge cases", h)); h += 1
        for ln in edge_cases.split("\n"):
            lines.append(f"  [{AMBER}]{ln}[/{AMBER}]")
        lines.append("")

    # Don't mix up with
    if confusion:
        lines.append(_sh("Don't mix up with", h)); h += 1
        for ln in confusion.split("\n"):
            lines.append(f"  [{DIM}]{ln}[/{DIM}]")
        lines.append("")

    # Follow-up questions
    if follow_up:
        lines.append(_sh("Follow-up questions", h)); h += 1
        for ln in follow_up.split("\n"):
            lines.append(f"  [{GOLD}]{ln}[/{GOLD}]")
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
        lines.append(
            "  " + "  ·  ".join(f"[{EMBER}]{r}[/{EMBER}]" for r in related)
        )
        lines.append("")

    # Notes
    if note.strip():
        lines.append(_sh("My Notes", h))
        for note_line in note.strip().split("\n"):
            lines.append(f"  {esc(note_line)}")
    else:
        lines.append(
            f"  [{DIM}]No notes yet — press [bold]N[/bold] to add one.[/{DIM}]"
        )

    return "\n".join(lines)
