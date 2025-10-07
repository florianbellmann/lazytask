from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.events import Key
from lazytask.presentation.widgets.text_area import TextArea


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

    def on_key(self, event: Key) -> None:
        """Handle keyboard shortcuts for submitting or cancelling the modal."""
        ctrl_pressed = bool(getattr(event, "ctrl", False))
        if event.key == "escape":
            event.stop()
            self.dismiss(None)
            return

        if event.key == "enter":
            if self.multiline and not ctrl_pressed:
                # Allow plain Enter to insert newlines when multiline is enabled.
                return

            event.stop()
            if self.multiline:
                self.dismiss(self.query_one(TextArea).text)
            else:
                self.dismiss(self.query_one(Input).value)
