import datetime
import pendulum

from textual.app import ComposeResult
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select_date":
            date_picker = self.query_one(DatePicker)
            self.dismiss(date_picker.date)
