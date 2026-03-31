"""Streamed Markdown → Rich markup conversion for agent session output."""

from __future__ import annotations

import re

# Strip Rich markup tags like [bold], [/dim], [#FF0000] before regex matching
MARKUP_RE = re.compile(r"\[/?[^\]]*\]")

# ── Markdown → Rich markup ─────────────────────────────────────────────────────
MD_FENCE_RE = re.compile(r"^```(\w*)")
_MD_HEADING_RE = re.compile(r"^#{1,3}\s+(.*)")
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_MD_HR_RE = re.compile(r"^[-]{3,}$")


def md_to_rich(line: str, in_code_block: bool) -> tuple[str, bool]:
    """Convert one streamed Markdown line to Rich markup.

    Returns (rendered_line, new_in_code_block). Handles:
      - ``` fences → dim language label / closing blank line
      - Code block content → escaped so Rich doesn't mis-parse brackets
      - ### headings → bold fire-orange
      - **bold** → [bold]…[/bold]
      - `inline code` → fire-orange
      - --- → dim horizontal rule
    """
    stripped = line.strip()

    # Code fence open/close
    fence_m = MD_FENCE_RE.match(stripped)
    if fence_m:
        if in_code_block:
            return "", False
        lang = fence_m.group(1) or "code"
        dashes = "─" * max(0, 14 - len(lang))
        return f"[dim]─── {lang} {dashes}[/dim]", True

    if in_code_block:
        # Escape [ so Rich doesn't try to parse code as markup
        return line.replace("[", r"\["), True

    # Horizontal rule — suppress (LLM-emitted --- adds visual noise before steps)
    if _MD_HR_RE.match(stripped):
        return "", False

    # Headings (# / ## / ###) → bold fire-orange, prefixed with blank line
    h = _MD_HEADING_RE.match(stripped)
    if h:
        title = _MD_BOLD_RE.sub(r"\1", h.group(1).strip())
        return f"\n[bold #FF8205]{title}[/bold #FF8205]", False

    # Inline: **bold** and `code`
    line = _MD_BOLD_RE.sub(r"[bold]\1[/bold]", line)
    line = _MD_INLINE_CODE_RE.sub(r"[#FF8205]\1[/#FF8205]", line)
    return line, False
