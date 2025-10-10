import datetime
import pendulum

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button
from textual_datepicker import DatePicker


class DatePickerScreen(ModalScreen[datetime.date | None]):
    """A modal screen to select a date."""

    _VIM_KEY_MAP = {
        "h": "left",
        "j": "down",
        "k": "up",
        "l": "right",
    }

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
        date_picker = self.query_one(DatePicker)
        date_picker.focus()
        self.call_after_refresh(self._focus_initial_day)

    def _focus_initial_day(self) -> None:
        date_picker = self.query_one(DatePicker)
        target_date = self.initial_date or datetime.date.today()
        pendulum_date = pendulum.instance(target_date)

        for day_label in date_picker.query("DayContainer DayLabel"):
            day = getattr(day_label, "day", None)
            if day == pendulum_date.day:
                day_label.focus()
                return

        for day_label in date_picker.query("DayContainer DayLabel"):
            if getattr(day_label, "day", None):
                day_label.focus()
                return

    def _dismiss_with_pendulum_date(
        self, pendulum_date: pendulum.DateTime | None
    ) -> None:
        if pendulum_date is None:
            self.dismiss(None)
            return
        python_date = datetime.date(
            pendulum_date.year, pendulum_date.month, pendulum_date.day
        )
        self.dismiss(python_date)

    def _dismiss_with_selected_date(self) -> None:
        date_picker = self.query_one(DatePicker)
        selected_date = getattr(date_picker, "selected_date", None)
        if selected_date is None:
            focused_day = getattr(date_picker, "focused_day", None)
            if focused_day is not None and getattr(focused_day, "day", None):
                selected_date = pendulum.datetime(
                    date_picker.date.year,
                    date_picker.date.month,
                    focused_day.day,
                )
            else:
                selected_date = date_picker.date
        self._dismiss_with_pendulum_date(selected_date)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select_date":
            self._dismiss_with_selected_date()

    def on_date_picker_selected(self, event: DatePicker.Selected) -> None:
        event.stop()
        self._dismiss_with_pendulum_date(event.date)

    def on_key(self, event: Key) -> None:
        if event.key in self._VIM_KEY_MAP:
            event.stop()
            mapped_key = self._VIM_KEY_MAP[event.key]
            self.query_one(DatePicker).post_message(Key(mapped_key, None))
        elif event.key == "escape":
            event.stop()
            self.dismiss(None)
