import datetime
import pendulum

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button
from textual_datepicker import DatePicker


class DatePickerScreen(ModalScreen[datetime.date | None]):
    """A modal screen to select a date."""

    def __init__(self, initial_date: datetime.date | None = None) -> None:
        super().__init__()
        self.initial_date = initial_date

    def compose(self) -> ComposeResult:
        date_picker = DatePicker()
        if self.initial_date:
            date_picker.date = pendulum.instance(self.initial_date)
        yield date_picker
        yield Button("Select", id="select_date")

    def on_mount(self) -> None:
        # Ensure the date picker receives focus for keyboard interaction.
        self.query_one(DatePicker).focus()

    def _dismiss_with_selected_date(self) -> None:
        date_picker = self.query_one(DatePicker)
        pendulum_date = date_picker.date
        if pendulum_date is None:
            self.dismiss(None)
            return
        python_date = datetime.date(
            pendulum_date.year, pendulum_date.month, pendulum_date.day
        )
        self.dismiss(python_date)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select_date":
            self._dismiss_with_selected_date()

    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            event.stop()
            self._dismiss_with_selected_date()
        elif event.key == "escape":
            event.stop()
            self.dismiss(None)
