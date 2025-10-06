from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label

from lazytask.presentation.widgets.text_area import TextArea


class TextInputModal(ModalScreen[str | None]):
    """A modal screen for text input."""

    def __init__(
        self, prompt: str, initial_value: str = "", multiline: bool = False
    ) -> None:
        super().__init__()
        self.prompt = prompt
        self.initial_value = initial_value
        self.multiline = multiline

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.prompt)
            if self.multiline:
                yield TextArea(text=self.initial_value, id="input")
            else:
                yield Input(value=self.initial_value, id="input")
            with Vertical(id="buttons"):
                yield Button("Submit", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "submit":
            if self.multiline:
                self.dismiss(self.query_one(TextArea).text)
            else:
                self.dismiss(self.query_one(Input).value)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        self.dismiss(event.value)
