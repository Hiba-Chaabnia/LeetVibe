"""Shared chat widgets — bubble transcript log and animated thinking indicator."""

from __future__ import annotations

from typing import Callable

from rich.panel import Panel
from rich.text import Text

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Collapsible, RichLog, Static

from leetvibe.ui.markup import esc, safe_markup_text
from leetvibe.ui.theme import AMBER, FIRE, GOLD, GRADIENT, RED, SHIMMER

_SPINNER_FRAMES: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ThinkingIndicator(Static):
    """Animated spinner + shimmering label ("thinking…" by default)."""

    def __init__(self, label: str = "thinking…", **kwargs) -> None:
        super().__init__("", **kwargs)
        self._label = label
        self._offset: int = 0
        self._frame: int = 0

    def set_label(self, label: str) -> None:
        self._label = label
        if self.display:
            self.update(self._build_text())

    def on_mount(self) -> None:
        self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        if not self.display:
            return
        self._offset = (self._offset + 1) % len(SHIMMER)
        self._frame = (self._frame + 1) % len(_SPINNER_FRAMES)
        self.update(self._build_text())

    def _build_text(self) -> Text:
        text = Text()
        text.append("  ")
        text.append(_SPINNER_FRAMES[self._frame], style=f"bold {FIRE}")
        text.append(" ")
        for i, ch in enumerate(self._label):
            color = SHIMMER[(i + self._offset) % len(SHIMMER)]
            text.append(ch, style=f"bold {color}")
        return text


class ChatBubbleLog(RichLog):
    """RichLog that renders conversation turns as titled bubble panels.

    ``renderer`` converts raw AI content (markdown, possibly with Rich markup)
    to a Rich markup string before display; user content is always escaped.
    """

    def __init__(
        self,
        *args,
        renderer: Callable[[str], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._renderer = renderer

    # ── Internals ─────────────────────────────────────────────────────

    def _render_content(self, content: str) -> Text:
        return safe_markup_text(content, self._renderer)

    def _write_panel(self, body, title: str, border: str) -> None:
        # expand=True on write: bubbles always span the log's full width
        # (RichLog otherwise sizes each renderable to its content).
        self.write(
            Panel(
                body,
                title=title,
                title_align="left",
                border_style=border,
                padding=(0, 1),
                expand=True,
            ),
            expand=True,
        )
        self.scroll_end(animate=False)

    # ── Bubbles ───────────────────────────────────────────────────────

    def append_user(self, message: str, speaker: str = "you") -> None:
        self._write_panel(
            esc(message), f"[bold {AMBER}] {speaker} [/bold {AMBER}]", AMBER
        )

    def append_ai(self, content: str, speaker: str = "leetvibe") -> None:
        self._write_panel(
            self._render_content(content),
            f"[bold {FIRE}] {speaker} [/bold {FIRE}]",
            FIRE,
        )

    def append_mnemonic(self, text: str) -> None:
        self._write_panel(
            Text.from_markup(f"[italic]{esc(text)}[/italic]"),
            f"[bold {GOLD}] 💡 mnemonic [/bold {GOLD}]",
            GOLD,
        )

    def append_error(self, message: str) -> None:
        self._write_panel(
            f"[{RED}]{esc(message)}[/{RED}]",
            f"[bold {RED}] error [/bold {RED}]",
            RED,
        )

    def append_raw(self, line: str) -> None:
        self.write(line)
        self.scroll_end(animate=False)

    # ── History ───────────────────────────────────────────────────────

    def restore_history(self, messages: list[dict], ai_speaker: str = "leetvibe") -> None:
        """Clear the log and re-render a saved conversation as bubbles."""
        self.clear()
        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content") or "").strip()
            if not content:
                continue
            if role == "user":
                self.append_user(content)
            elif role == "assistant":
                self.append_ai(content, speaker=ai_speaker)


class StepAnswerBubble(Vertical):
    """Bubble-styled container for a Learn/Pair step-by-step answer — one
    Collapsible per step (all expanded initially; the user collapses them
    manually), each step's header — including its collapse/expand arrow, not
    just the title text — colored by its position in the brand gradient.

    Mounted directly into the transcript rather than written into a
    ChatBubbleLog: Collapsible is a live, clickable widget, and RichLog only
    ever rasterizes a static snapshot of whatever's written to it — it has
    no way to host an interactive child, so this can't just be another
    append_* call on the log.

    Coloring is done via a per-step "grad-N" CSS class (see main.tcss)
    rather than inline [bold #hex] markup on the title string: Collapsible
    assembles its arrow symbol and label as two independently-styled pieces
    (textual.widgets._collapsible.CollapsibleTitle._update_label uses
    Content.assemble(symbol, " ", label), and a bare str part there is
    inserted as literal, unstyled text) — so markup on the label alone can
    only ever color the text, never the arrow next to it. Styling the whole
    CollapsibleTitle by CSS class colors both pieces from one source.

    The arrow sits after the title text, not before it: Collapsible always
    assembles symbol-then-label with no way to reverse that via public API,
    so collapsed_symbol/expanded_symbol are set to "" (dropping the built-in
    left-side arrow) and the arrow is appended to `title` instead, updated
    on Collapsible.Toggled — the one hook this doesn't need Collapsible's
    private internals for.
    """

    _COLLAPSED_ARROW = "▶"
    _EXPANDED_ARROW = "▼"

    def __init__(
        self,
        speaker: str,
        steps: list[dict],
        renderer: Callable[[str], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.border_title = f" {speaker} "
        self._steps = steps
        self._renderer = renderer

    def compose(self) -> ComposeResult:
        for step in self._steps:
            idx = (step["num"] - 1) % len(GRADIENT)
            base_title = esc(f"Step {step['num']} — {step['title']}")
            collapsible = Collapsible(
                title=f"{base_title}  {self._EXPANDED_ARROW}",
                collapsed=False,
                collapsed_symbol="",
                expanded_symbol="",
                classes=f"grad-{idx}",
            )
            collapsible._step_base_title = base_title  # read back in on_collapsible_toggled
            with collapsible:
                yield Static(safe_markup_text(step["content"], self._renderer))

    def on_collapsible_collapsed(self, event: Collapsible.Collapsed) -> None:
        self._update_arrow(event.collapsible)

    def on_collapsible_expanded(self, event: Collapsible.Expanded) -> None:
        self._update_arrow(event.collapsible)

    def _update_arrow(self, c: Collapsible) -> None:
        base = getattr(c, "_step_base_title", None)
        if base is None:
            return
        arrow = self._COLLAPSED_ARROW if c.collapsed else self._EXPANDED_ARROW
        c.title = f"{base}  {arrow}"
