"""Shared Markdown → Rich markup rendering for chat bubbles and content panes."""

from __future__ import annotations

import re

from leetvibe.ui.theme import AMBER, DIM, FIRE, RED

# Strip Rich markup tags like [bold], [/dim], [#FF0000]
MARKUP_RE = re.compile(r"\[/?[^\]]*\]")

# Rich [bold]…[/bold] emitted by the agent — normalised to markdown before stripping
_RICH_BOLD_RE = re.compile(r"\[bold\](.+?)\[/bold\]", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_MD_HEADING_RE = re.compile(r"^#{1,3}\s+(.*)")
_MD_HR_RE = re.compile(r"^-{3,}$")

# Lines starting with a tool icon are agent tool-call headers; "│" and the box
# corners mark their indented detail/table lines. All render dim (red when the
# line carries a ✗ failure).
_TOOL_LINE_PREFIXES = ("▶", "◈", "✎", "⚙", "│", "┌", "├", "└")


def esc(text: str) -> str:
    """Escape [ so Rich doesn't interpret content as markup tags."""
    return text.replace("[", r"\[")


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
    passed through untouched, headings render fire-orange, and tool-summary
    lines (▶/◈/✎ prefix) render dim.
    """
    lines_out: list[str] = []
    in_code = False
    code_lines: list[str] = []

    for line in content.split("\n"):
        if line.strip().startswith("```"):
            if in_code:
                for rendered in code_block("\n".join(code_lines), width=40):
                    lines_out.append(rendered)
                lines_out.append("")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        raw = line.rstrip()
        # Tool header/detail lines render verbatim BEFORE tag-stripping —
        # test outputs like [1,2,0] would otherwise be eaten as Rich tags.
        if raw.strip().startswith(_TOOL_LINE_PREFIXES):
            color = RED if ("✗" in raw or "failed" in raw) else DIM
            lines_out.append(f"[{color}]{esc(raw)}[/{color}]")
            continue

        # Normalise the full line (keeps indentation for nested lists)
        norm = _strip_rich_markup(raw)
        stripped = norm.strip()
        if not stripped:
            lines_out.append("")
        elif _MD_HR_RE.match(stripped):
            continue  # LLM-emitted --- rules add visual noise
        elif (h := _MD_HEADING_RE.match(stripped)):
            title = re.sub(r"\*\*(.+?)\*\*", r"\1", h.group(1).strip())
            lines_out.append(f"[bold {FIRE}]{esc(title)}[/bold {FIRE}]")
        else:
            lines_out.append(md_inline(norm))

    if in_code and code_lines:
        for rendered in code_block("\n".join(code_lines), width=40):
            lines_out.append(rendered)

    while lines_out and not lines_out[-1].strip():
        lines_out.pop()
    while lines_out and not lines_out[0].strip():
        lines_out.pop(0)

    return "\n".join(lines_out)
