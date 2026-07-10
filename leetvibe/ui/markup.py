"""Shared Markdown → Rich markup rendering for chat bubbles and content panes."""

from __future__ import annotations

import re
from typing import Callable

from rich.text import Text

from leetvibe.ui.theme import AMBER, DIM, FIRE, GRADIENT, RED

# Strip Rich markup tags like [bold], [/dim], [#FF0000]
MARKUP_RE = re.compile(r"\[/?[^\]]*\]")

# Rich [bold]…[/bold] emitted by the agent — normalised to markdown before stripping
_RICH_BOLD_RE = re.compile(r"\[bold\](.+?)\[/bold\]", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_MD_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)")
_MD_HR_RE = re.compile(r"^-{3,}$")
# Matches the "Step N — …" text inside a "### Step N — Title" heading
# (session.py's _post_answer_bubble synthesises these) so each step gets a
# distinct color cycling through the brand gradient instead of one flat FIRE.
_STEP_HEADING_RE = re.compile(r"^Step\s+(\d+)\b", re.IGNORECASE)

# Tool-call summary/header lines ("▶ run_code — 3/3 tests failed") — red when
# the run actually failed, dim otherwise.
_TOOL_HEADER_PREFIXES = ("▶", "◈", "✎", "⚙")
# Box-drawing table rows underneath a header line — always dim. A passing
# case's own row can legitimately contain the word "failed" as plain data (a
# neighboring case's status cell, or test content), so unlike the header this
# is never colored by string-matching "failed" — that turned entire tables
# red just because *some* row failed, not because that row itself did.
_TOOL_LINE_PREFIXES = _TOOL_HEADER_PREFIXES + ("│", "┌", "├", "└")

_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_CODE_RE = re.compile(r"`([^`]+)`")


def esc(text: str) -> str:
    """Escape [ so Rich doesn't interpret content as markup tags."""
    return text.replace("[", r"\[")


def safe_markup_text(content: str, renderer: Callable[[str], str] | None = None) -> Text:
    """Render *content* through *renderer* (or escape it) to Rich markup, then
    parse it into a Text object — falling back to plain, tag-stripped text if
    the model ever emits malformed/unbalanced markup. Shared by every widget
    that displays AI content (ChatBubbleLog, StepAnswerBubble) so a bad-markup
    guard can't silently drift between separately-maintained copies.
    """
    markup = renderer(content) if renderer else esc(content)
    try:
        return Text.from_markup(markup)
    except Exception:
        return Text(MARKUP_RE.sub("", markup))


def md_inline(line: str) -> str:
    """Convert inline markdown to Rich markup, safely escaping literal brackets."""
    line = line.replace("[", "\x00")
    line = re.sub(r"\*\*(.+?)\*\*", r"[bold]\1[/bold]", line)
    line = re.sub(r"`([^`]+)`", rf"[bold {AMBER}]\1[/bold {AMBER}]", line)
    if re.match(r"^[-•]\s", line):
        line = f"  [{DIM}]•[/{DIM}] " + line[2:]
    line = line.replace("\x00", r"\[")
    return line


def code_block(block: str, width: int = 24) -> list[str]:
    """Render a code block with box-drawing header and │-prefixed lines."""
    # "  ┌── python " = 13 chars; fill rest with dashes up to total width
    dash_header = max(2, width - 13)
    dash_footer = max(2, width - 3)
    lines = [f"  [{DIM}]┌── python {'─' * dash_header}[/{DIM}]"]
    for ln in block.split("\n"):
        # Escape code brackets — nums[i] must not switch on Rich italic
        lines.append(f"  [{DIM}]│[/{DIM}] {esc(ln)}")
    lines.append(f"  [{DIM}]└{'─' * dash_footer}[/{DIM}]")
    return lines


def _looks_like_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def _is_table_separator(line: str) -> bool:
    """Match a "| --- | :-: |"-style divider row following a table header."""
    s = line.strip()
    if not s or set(s) - set("|-: "):
        return False
    return "-" in s


def _parse_table_row(line: str) -> list[str]:
    inner = line.strip()[1:-1]  # drop leading/trailing "|"
    cells = [c.strip() for c in inner.split("|")]
    return [_MD_CODE_RE.sub(r"\1", _MD_BOLD_RE.sub(r"\1", c)) for c in cells]


def table_block(rows: list[list[str]]) -> list[str]:
    """Render parsed markdown-table rows as a box-drawing table, matching the
    tool-result table style (agent.py's _tool_table) so a model-emitted
    "| Aspect | ... |" comparison table looks the same as a run_code table
    instead of printing as raw, unaligned pipe characters."""
    ncols = max(len(r) for r in rows)
    norm_rows = [r + [""] * (ncols - len(r)) for r in rows]
    widths = [max(len(r[i]) for r in norm_rows) for i in range(ncols)]

    def _row(cells: list[str]) -> str:
        return "│ " + " │ ".join(esc(c).ljust(w) for c, w in zip(cells, widths)) + " │"

    top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    return [top, _row(norm_rows[0]), mid, *(_row(r) for r in norm_rows[1:]), bot]


def render_response_to_markup(content: str) -> str:
    """Convert AI response markdown to a Rich markup string for Panel display."""
    lines_out: list[str] = []
    in_code = False
    code_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("```"):
            if in_code:
                for rendered in code_block("\n".join(code_lines), width=22):
                    lines_out.append(rendered)
                lines_out.append("")
                code_lines = []
                in_code = False
            else:
                in_code = True
        elif in_code:
            code_lines.append(line)
        elif line.strip():
            lines_out.append(md_inline(line))
        else:
            lines_out.append("")

    if in_code and code_lines:
        for rendered in code_block("\n".join(code_lines), width=22):
            lines_out.append(rendered)

    while lines_out and not lines_out[-1].strip():
        lines_out.pop()

    return "\n".join(lines_out)


def _strip_rich_markup(line: str) -> str:
    """Normalise a prose line from the agent: [bold]→**…**, drop other Rich tags.

    Inline `code` spans are protected first so indexing like `nums[0]` survives.
    """
    spans: list[str] = []

    def _stash(m: re.Match) -> str:
        spans.append(m.group(0))
        return f"\x01{len(spans) - 1}\x01"

    line = _INLINE_CODE_RE.sub(_stash, line)
    line = _RICH_BOLD_RE.sub(r"**\1**", line)
    line = MARKUP_RE.sub("", line)
    for i, span in enumerate(spans):
        line = line.replace(f"\x01{i}\x01", span)
    return line


def render_agent_markup(content: str) -> str:
    """Agent-session variant of render_response_to_markup.

    The agent's system prompt tells the model to emit Rich markup ([bold]/[dim])
    on top of markdown, so prose lines are normalised ([bold]→**…**, other tags
    dropped) before the bracket-escaping markdown pipeline runs. Code blocks are
    passed through untouched, "Step N — …" headings cycle through the brand
    gradient by step number, other headings render fire-orange, and tool-summary
    lines (▶/◈/✎ prefix) render dim.
    """
    lines_out: list[str] = []
    in_code = False
    code_lines: list[str] = []

    raw_lines = content.split("\n")
    n = len(raw_lines)
    i = 0
    while i < n:
        line = raw_lines[i]
        if line.strip().startswith("```"):
            if in_code:
                for rendered in code_block("\n".join(code_lines), width=40):
                    lines_out.append(rendered)
                lines_out.append("")
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        raw = line.rstrip()

        # A markdown table (header row + "|---|---|" divider) — buffer every
        # subsequent "|…|" row and render the block as a box-drawing table,
        # matching format_tool_block's run_code/analyze_complexity tables
        # instead of printing raw, unaligned pipes.
        if (
            _looks_like_table_row(raw)
            and i + 1 < n
            and _is_table_separator(raw_lines[i + 1])
        ):
            table_rows = [_parse_table_row(raw)]
            j = i + 2
            while j < n and _looks_like_table_row(raw_lines[j]):
                table_rows.append(_parse_table_row(raw_lines[j]))
                j += 1
            for tline in table_block(table_rows):
                lines_out.append(f"[{DIM}]{tline}[/{DIM}]")
            i = j
            continue

        # Tool header/detail lines render verbatim BEFORE tag-stripping —
        # test outputs like [1,2,0] would otherwise be eaten as Rich tags.
        if raw.strip().startswith(_TOOL_LINE_PREFIXES):
            is_header = raw.strip().startswith(_TOOL_HEADER_PREFIXES)
            color = RED if is_header and "failed" in raw else DIM
            lines_out.append(f"[{color}]{esc(raw)}[/{color}]")
            i += 1
            continue

        # Normalise the full line (keeps indentation for nested lists)
        norm = _strip_rich_markup(raw)
        stripped = norm.strip()
        if not stripped:
            lines_out.append("")
        elif _MD_HR_RE.match(stripped):
            pass  # LLM-emitted --- rules add visual noise
        elif (h := _MD_HEADING_RE.match(stripped)):
            title = re.sub(r"\*\*(.+?)\*\*", r"\1", h.group(1).strip())
            step_m = _STEP_HEADING_RE.match(title)
            color = GRADIENT[(int(step_m.group(1)) - 1) % len(GRADIENT)] if step_m else FIRE
            lines_out.append(f"[bold {color}]{esc(title)}[/bold {color}]")
        else:
            lines_out.append(md_inline(norm))
        i += 1

    if in_code and code_lines:
        for rendered in code_block("\n".join(code_lines), width=40):
            lines_out.append(rendered)

    while lines_out and not lines_out[-1].strip():
        lines_out.pop()
    while lines_out and not lines_out[0].strip():
        lines_out.pop(0)

    return "\n".join(lines_out)
