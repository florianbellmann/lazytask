from __future__ import annotations

import re
from typing import ClassVar

from rich.style import Style
from rich.text import Text

from textual import on
from textual.geometry import clamp, Region, Size
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.binding import Binding, BindingType
from textual.widget import Widget
from textual.events import Key


class TextEditor(Widget):
    """The protocol for a text editor widget."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("left", "cursor_left", "cursor left", show=False),
        Binding("right", "cursor_right", "cursor right", show=False),
        Binding("up", "cursor_up", "cursor up", show=False),
        Binding("down", "cursor_down", "cursor down", show=False),
        Binding("ctrl+left", "cursor_left_word", "cursor left word", show=False),
        Binding("ctrl+right", "cursor_right_word", "cursor right word", show=False),
        Binding("home,ctrl+a", "cursor_line_start", "cursor line start", show=False),
        Binding("end,ctrl+e", "cursor_line_end", "cursor line end", show=False),
        Binding("backspace", "delete_left", "delete left", show=False),
        Binding("ctrl+d", "delete_right", "delete right", show=False),
        Binding("enter", "insert_newline", "insert newline", show=False),
    ]
    """The default bindings for the text editor."""

    text: reactive[str] = reactive("")
    """The text content of the editor."""

    def insert_text(self, text: str) -> None:
        """Insert text at the cursor position."""
        raise NotImplementedError

    def delete_left(self) -> None:
        """Delete the character to the left of the cursor."""
        raise NotImplementedError

    def delete_right(self) -> None:
        """Delete the character to the right of the cursor."""
        raise NotImplementedError

    def move_cursor(self, x: int, y: int) -> None:
        """Move the cursor to a new position."""
        raise NotImplementedError

    def move_cursor_relative(self, x: int = 0, y: int = 0) -> None:
        """Move the cursor relative to its current position."""
        raise NotImplementedError


class TextArea(ScrollableContainer, TextEditor):
    """A simple text area widget."""

    DEFAULT_CSS = """
    TextArea {
        background: $panel;
        color: $text;
        width: auto;
        height: auto;
    }
    """

    def __init__(
        self,
        text: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._cursor_position = (0, 0)
        self.text = text
        self._lines: list[str] = []

    def _watch_text(self, text: str) -> None:
        self._lines = text.split('\n')
        self.virtual_size = Size(
            max(len(line) for line in self._lines) if self._lines else 0,
            len(self._lines),
        )
        self.move_cursor(self.cursor_position[0], self.cursor_position[1])
        self.refresh()

    @property
    def cursor_position(self) -> tuple[int, int]:
        """The position of the cursor."""
        return self._cursor_position

    def move_cursor(self, x: int, y: int) -> None:
        """Move the cursor to a new position."""
        x = clamp(x, 0, len(self._lines[y]) if self._lines else 0)
        y = clamp(y, 0, len(self._lines) - 1 if self._lines else 0)
        self._cursor_position = (x, y)
        self.scroll_to_region(self.cursor_region, animate=True, spacing=(2, 2, 2, 2))
        self.refresh()

    def move_cursor_relative(self, x: int = 0, y: int = 0) -> None:
        """Move the cursor relative to its current position."""
        cx, cy = self.cursor_position
        self.move_cursor(cx + x, cy + y)

    def insert_text(self, text: str) -> None:
        """Insert text at the cursor position."""
        cx, cy = self.cursor_position
        lines = self._lines
        if not lines:
            lines.append("")
        line = lines[cy]
        lines[cy] = line[:cx] + text + line[cx:]
        self.text = "\n".join(lines)
        self.move_cursor(cx + len(text), cy)

    def delete_left(self) -> None:
        """Delete the character to the left of the cursor."""
        cx, cy = self.cursor_position
        if cx > 0:
            line = self._lines[cy]
            self._lines[cy] = line[: cx - 1] + line[cx:]
            self.text = "\n".join(self._lines)
            self.move_cursor(cx - 1, cy)
        elif cy > 0:
            line = self._lines.pop(cy)
            prev_line_len = len(self._lines[cy - 1])
            self._lines[cy - 1] += line
            self.text = "\n".join(self._lines)
            self.move_cursor(prev_line_len, cy - 1)

    def delete_right(self) -> None:
        """Delete the character to the right of the cursor."""
        cx, cy = self.cursor_position
        line = self._lines[cy]
        if cx < len(line):
            self._lines[cy] = line[:cx] + line[cx + 1 :]
            self.text = "\n".join(self._lines)
            self.move_cursor(cx, cy)
        elif cy < len(self._lines) - 1:
            self._lines[cy] += self._lines.pop(cy + 1)
            self.text = "\n".join(self._lines)
            self.move_cursor(cx, cy)

    def action_cursor_left(self) -> None:
        """Move the cursor left."""
        self.move_cursor_relative(x=-1)

    def action_cursor_right(self) -> None:
        """Move the cursor right."""
        self.move_cursor_relative(x=1)

    def action_cursor_up(self) -> None:
        """Move the cursor up."""
        self.move_cursor_relative(y=-1)

    def action_cursor_down(self) -> None:
        """Move the cursor down."""
        self.move_cursor_relative(y=1)

    def action_cursor_left_word(self) -> None:
        """Move the cursor left by a word."""
        cx, cy = self.cursor_position
        line = self._lines[cy]
        if cx > 0:
            match = re.search(r"\w+\W*$", line[:cx])
            if match:
                self.move_cursor(match.start(), cy)
            else:
                self.move_cursor(0, cy)
        elif cy > 0:
            self.move_cursor(len(self._lines[cy - 1]), cy - 1)

    def action_cursor_right_word(self) -> None:
        """Move the cursor right by a word."""
        cx, cy = self.cursor_position
        line = self._lines[cy]
        if cx < len(line):
            match = re.search(r"\w+\W*", line[cx:])
            if match:
                self.move_cursor(cx + match.end(), cy)
            else:
                self.move_cursor(len(line), cy)
        elif cy < len(self._lines) - 1:
            self.move_cursor(0, cy + 1)

    def action_cursor_line_start(self) -> None:
        """Move the cursor to the start of the line."""
        self.move_cursor(0, self.cursor_position[1])

    def action_cursor_line_end(self) -> None:
        """Move the cursor to the end of the line."""
        self.move_cursor(len(self._lines[self.cursor_position[1]]), self.cursor_position[1])

    def action_delete_left(self) -> None:
        """Delete the character to the left of the cursor."""
        self.delete_left()

    def action_delete_right(self) -> None:
        """Delete the character to the right of the cursor."""
        self.delete_right()

    def action_insert_newline(self) -> None:
        """Insert a newline at the cursor position."""
        cx, cy = self.cursor_position
        if not self._lines:
            self._lines.append("")
        line = self._lines[cy]
        self._lines.insert(cy + 1, line[cx:])
        self.text = "\n".join(self._lines)
        self.move_cursor(0, cy + 1)

    def render_line(self, y: int) -> Text:
        """Render a single line of the text area."""
        line = self._lines[y] if y < len(self._lines) else ""
        text = Text(line, end="")
        if y == self.cursor_position[1]:
            text.stylize("bold", self.cursor_position[0], self.cursor_position[0] + 1)
        return text

    def render(self) -> list[Text]:
        """Render the text area."""
        return [self.render_line(y) for y in range(self.virtual_size[1])]

    @property
    def cursor_region(self) -> Region:
        """The region of the cursor."""
        x, y = self.cursor_position
        return Region(x, y, 1, 1)

    @on(Widget.focus)
    def _on_focus(self) -> None:
        self.refresh()

    @on(Widget.blur)
    def _on_blur(self) -> None:
        self.refresh()

    def on_key(self, event: Key) -> None:
        """Handle key presses."""
        if event.is_printable and event.character:
            self.insert_text(event.character)
            event.prevent_default()
            event.stop()
