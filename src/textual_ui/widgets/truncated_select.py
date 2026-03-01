"""TruncatedSelect — Select widget that clips its label with … on overflow."""

from __future__ import annotations

from textual.widgets import Select, Static


def _truncate(text: str, max_chars: int, ellipsis: str = "…") -> str:
    if len(text) <= max_chars:
        return text
    keep = max(0, max_chars - len(ellipsis))
    return text[:keep] + ellipsis


class TruncatedSelect(Select):
    """A Select that truncates the displayed label to fit its container width."""

    def __init__(self, options: list[tuple[str, str]], **kwargs) -> None:
        super().__init__(options, **kwargs)
        self._option_map: dict[str, str] = {str(val): label for label, val in options}

    def _label_for(self, value: object) -> str | None:
        if value is Select.BLANK:
            return None
        return self._option_map.get(str(value))

    def _apply_truncation(self) -> None:
        try:
            label_widget = self.query_one("SelectCurrent #label", Static)
        except Exception:
            return
        raw = self._label_for(self.value)
        if raw is None:
            return
        available = max(4, self.size.width - 9)
        label_widget.update(_truncate(raw, available))

    def set_options(self, options) -> None:  # type: ignore[override]
        super().set_options(options)
        self._option_map = {str(val): str(label) for label, val in options}
        self.call_after_refresh(self._apply_truncation)

    def on_mount(self) -> None:
        self.call_after_refresh(self._apply_truncation)

    def on_resize(self) -> None:
        self._apply_truncation()

    def watch_value(self, value: object) -> None:
        self.call_after_refresh(self._apply_truncation)
