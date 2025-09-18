from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static


class HelpScreen(ModalScreen):
    """A screen to display help information."""

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        if self.parent:
            bindings = self.parent.BINDINGS
            text = []
            for binding in bindings:
                text.append(f"{binding.key.upper()}: {binding.description}")
            yield Static("\n".join(text), id="help-text")
        else:
            yield Static("No help available.", id="help-text")
