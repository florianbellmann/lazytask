from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static

class HelpScreen(ModalScreen):
    """A screen to display help information."""

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        bindings = self.parent.BINDINGS
        text = "\n".join([f"{key.upper()}: {description}" for key, _, description in bindings])
        yield Static(text, id="help-text")
