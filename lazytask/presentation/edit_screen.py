import datetime

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Switch
from textual.containers import Vertical

from lazytask.domain.task import Task
from lazytask.presentation.date_picker_screen import DatePickerScreen


class EditScreen(ModalScreen[Task]):
    """Screen to edit a task."""

    def __init__(self, task: Task) -> None:
        super().__init__()
        self._task = task

    def compose(self) -> ComposeResult:
        with Vertical(id="edit-task-dialog") as container:
            container.border_title = "Edit Task"
            yield Label("Description:")
            yield Input(value=self._task.description or "", id="description")
            yield Label("Tags (comma-separated):")
            yield Input(value=",".join(self._task.tags), id="tags")
            yield Label("Priority:")
            yield Input(value=str(self._task.priority or ""), id="priority")
            yield Label("Flagged:")
            yield Switch(value=self._task.is_flagged, id="flagged")
            yield Label("Due Date:")
            yield Label(str(self._task.due_date) if self._task.due_date else "No due date", id="due-date-label")
            yield Button("Edit Due Date", id="edit-due-date")
            yield Button("Save", variant="primary", id="save")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._task.description = self.query_one("#description", Input).value
            self._task.tags = [tag.strip() for tag in self.query_one("#tags", Input).value.split(",")]
            priority_str = self.query_one("#priority", Input).value
            try:
                self._task.priority = int(priority_str) if priority_str else None
            except ValueError:
                self.app.notify("Invalid priority. Please enter a number.", title="Error", severity="error")
                return
            self._task.is_flagged = self.query_one("#flagged", Switch).value
            self.dismiss(self._task)
        elif event.button.id == "edit-due-date":
            def on_date_selected(new_date: datetime.date | None):
                self._task.due_date = new_date
                self.query_one("#due-date-label", Label).update(str(new_date) if new_date else "No due date")

            self.app.push_screen(DatePickerScreen(initial_date=self._task.due_date), on_date_selected)
        else:
            self.dismiss()
