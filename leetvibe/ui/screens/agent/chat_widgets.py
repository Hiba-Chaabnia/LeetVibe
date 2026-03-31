"""Chat widgets for the agent session — message bubbles, steps, code blocks."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalGroup, VerticalScroll
from textual.widgets import Button, Static

from leetvibe.ui.theme import FIRE, GRADIENT, SHIMMER

from .markdown import MD_FENCE_RE, md_to_rich


class ChatScroll(VerticalScroll):
    """Performance-optimised scroll container — skips cascading style recalcs."""

    def update_node_styles(self, animate: bool = True) -> None:  # noqa: FBT001
        pass


class UserMessage(Static):
    """User / problem turn: orange heavy left-border bubble."""

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def compose(self) -> ComposeResult:
        yield Static(self._text, markup=True, classes="msg-content")


class CopyableCodeBlock(Static):
    """Inline code block with a one-click ⎘ copy button."""

    def __init__(self, lang: str) -> None:
        super().__init__()
        self._lang = lang or "code"
        self._lines: list[str] = []
        self._body: Static | None = None
        self._btn: Button | None = None

    def compose(self) -> ComposeResult:
        dashes = "─" * max(0, 14 - len(self._lang))
        with Horizontal(classes="cb-header"):
            yield Static(
                f"[dim]─── {self._lang} {dashes}[/dim]",
                markup=True, classes="cb-lang",
            )
            self._btn = Button("⎘", classes="cb-btn")
            yield self._btn
        self._body = Static("", markup=False, classes="cb-body")
        yield self._body

    def add_line(self, line: str) -> None:
        self._lines.append(line)
        if self._body is not None:
            try:
                self._body.update("\n".join(self._lines))
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.copy_to_clipboard("\n".join(self._lines))
        event.stop()
        if self._btn is not None:
            self._btn.label = "✓"
            self.set_timer(1.5, self._reset_btn)

    def _reset_btn(self) -> None:
        if self._btn is not None:
            self._btn.label = "⎘"


def _write_line_to_container(
    line: str,
    container: "VerticalGroup",
    text_lines: list[str],
    text_widget_ref: list["Static | None"],
    code_block_ref: list["CopyableCodeBlock | None"],
    in_code_block_ref: list[bool],
) -> None:
    """Shared logic: route a streamed line into a VerticalGroup as text or code widget."""
    stripped = line.strip()
    fence_m = MD_FENCE_RE.match(stripped)

    if fence_m:
        if in_code_block_ref[0]:
            # Close code block — start a fresh text segment
            in_code_block_ref[0] = False
            code_block_ref[0] = None
            new_text = Static("", markup=True, classes="step-text")
            text_widget_ref[0] = new_text
            text_lines.clear()
            try:
                container.mount(new_text)
            except Exception:
                pass
        else:
            # Open code block
            lang = fence_m.group(1) or "code"
            in_code_block_ref[0] = True
            cb = CopyableCodeBlock(lang)
            code_block_ref[0] = cb
            try:
                container.mount(cb)
            except Exception:
                pass
        return

    if in_code_block_ref[0]:
        if code_block_ref[0] is not None:
            code_block_ref[0].add_line(line)
    else:
        rendered, _ = md_to_rich(line, False)
        text_lines.append(rendered)
        tw = text_widget_ref[0]
        if tw is not None:
            try:
                tw.update("\n".join(text_lines))
            except Exception:
                pass


class BackgroundStep(Static):
    """Steps 1-7 and 9+: shimmer spinner header + collapsible content (hidden by default)."""

    SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, step_num: int, title: str, content_visible: bool = False) -> None:
        super().__init__()
        self._step_num = step_num
        self._title = title
        self._tick = 0
        self._done = False
        self._done_color: str = GRADIENT[0]
        self._content_visible = content_visible
        self._header_widget: Static | None = None
        self._content_container: VerticalGroup | None = None
        # Mutable refs passed to the shared write helper
        self._text_lines: list[str] = []
        self._text_widget_ref: list[Static | None] = [None]
        self._code_block_ref: list[CopyableCodeBlock | None] = [None]
        self._in_code_block_ref: list[bool] = [False]

    def compose(self) -> ComposeResult:
        self._header_widget = Static(self._render_header(), markup=True, classes="step-header")
        yield self._header_widget
        self._content_container = VerticalGroup(classes="step-content")
        yield self._content_container

    def on_mount(self) -> None:
        if self._content_container is not None:
            self._content_container.display = self._content_visible
            init_text = Static("", markup=True, classes="step-text")
            self._text_widget_ref[0] = init_text
            self._content_container.mount(init_text)

    def _shimmer_text(self, text: str) -> str:
        parts: list[str] = []
        n = len(SHIMMER)
        for i, ch in enumerate(text):
            color = SHIMMER[(self._tick + i) % n]
            safe = ch.replace("[", r"\[")
            parts.append(f"[bold {color}]{safe}[/bold {color}]")
        return "".join(parts)

    def _render_header(self) -> str:
        if self._done:
            color = self._done_color
            icon = f"[bold {color}]✓[/bold {color}]"
            return f"{icon} [{color}]Step {self._step_num} — {self._title}[/{color}]"
        spinner_ch = self.SPINNER[self._tick % len(self.SPINNER)]
        return self._shimmer_text(f"{spinner_ch} Step {self._step_num} — {self._title}")

    def advance_spinner(self) -> None:
        if not self._done:
            self._tick += 1
            if self._header_widget is not None:
                try:
                    self._header_widget.update(self._render_header())
                except Exception:
                    pass

    def mark_done(self) -> None:
        self._done = True
        self._done_color = GRADIENT[(self._step_num - 1) % len(GRADIENT)]
        if self._header_widget is not None:
            try:
                self._header_widget.update(self._render_header())
            except Exception:
                pass

    def write_line(self, line: str) -> None:
        if self._content_container is None:
            return
        _write_line_to_container(
            line, self._content_container,
            self._text_lines, self._text_widget_ref,
            self._code_block_ref, self._in_code_block_ref,
        )

    def toggle_content(self, visible: bool) -> None:
        self._content_visible = visible
        if self._content_container is not None:
            self._content_container.display = visible


class FinalAnswer(Static):
    """Final synthesis step: always fully visible, supports copyable code blocks."""

    def __init__(self, step_num: int, title: str) -> None:
        super().__init__()
        self._step_num = step_num
        self._title = title
        self._content_container: VerticalGroup | None = None
        self._all_lines: list[str] = []   # raw lines kept for narration
        self._text_lines: list[str] = []
        self._text_widget_ref: list[Static | None] = [None]
        self._code_block_ref: list[CopyableCodeBlock | None] = [None]
        self._in_code_block_ref: list[bool] = [False]

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold {FIRE}]━━  Step {self._step_num} — {self._title}  ━━[/bold {FIRE}]",
            markup=True,
            classes="final-sep",
        )
        self._content_container = VerticalGroup(classes="final-content")
        yield self._content_container

    def on_mount(self) -> None:
        if self._content_container is not None:
            init_text = Static("", markup=True, classes="step-text")
            self._text_widget_ref[0] = init_text
            self._content_container.mount(init_text)

    def write_line(self, line: str) -> None:
        self._all_lines.append(line)
        if self._content_container is None:
            return
        _write_line_to_container(
            line, self._content_container,
            self._text_lines, self._text_widget_ref,
            self._code_block_ref, self._in_code_block_ref,
        )


class AssistantBlock(Static):
    """One follow-up AI turn (or fallback block): accumulates streamed Rich-markup lines."""

    def __init__(self) -> None:
        super().__init__()
        self._lines: list[str] = []
        self._in_code_block = False
        self._display: Static | None = None

    def compose(self) -> ComposeResult:
        self._display = Static("", markup=True)
        yield self._display

    def on_mount(self) -> None:
        # Flush any lines that arrived before compose() ran
        if self._lines and self._display is not None:
            self._display.update("\n".join(self._lines))

    def write_line(self, line: str) -> None:
        rendered, self._in_code_block = md_to_rich(line, self._in_code_block)
        self._lines.append(rendered)
        if self._display is not None:
            try:
                self._display.update("\n".join(self._lines))
            except Exception:
                pass
