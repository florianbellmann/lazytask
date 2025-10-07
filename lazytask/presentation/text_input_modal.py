from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, TextArea
from textual.events import Key


class TextInputModal(ModalScreen[str | None]):
    """A modal screen for text input."""

    def __init__(
        self,
        prompt: str,
        initial_value: str = "",
        multiline: bool = False,
    ) -> None:
        super().__init__()
        self.prompt = prompt
        self.initial_value = initial_value
        self.multiline = multiline
        if self.multiline:
            self.input_widget = TextArea(text=self.initial_value, id="input")
        else:
            self.input_widget = Input(value=self.initial_value, id="input")

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.prompt)
            yield self.input_widget
            with Vertical(id="buttons"):
                yield Button("Submit", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.input_widget.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "submit":
            if self.multiline:
                self.dismiss(self.query_one(TextArea).text)
            else:
                self.dismiss(self.query_one(Input).value)
        else:
            self.dismiss(None)
