from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static
from textual.binding import Binding
from typing import cast, Tuple


class HelpScreen(ModalScreen):
    """A screen to display help information."""

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        if self.parent:
            bindings = self.parent.BINDINGS
            text = []
            for binding in bindings:
                if isinstance(binding, Binding):
                    text.append(f"{binding.key.upper()}: {binding.description}")
                else:
                    key, action, description = cast(Tuple[str, str, str], binding)
                    text.append(f"{key.upper()}: {description}")
            yield Static("\n".join(text), id="help-text")
        else:
            yield Static("No help available.", id="help-text")
