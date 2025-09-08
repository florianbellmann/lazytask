from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Switch
from textual.containers import Vertical

from lazytask.domain.task import Task

class EditScreen(ModalScreen[Task]):
    """Screen to edit a task."""

    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task

    def compose(self) -> ComposeResult:
        with Vertical(id="edit-task-dialog") as container:
            container.border_title = "Edit Task"
            yield Label("Description:")
            yield Input(value=self.task.description or "", id="description")
            yield Label("Tags (comma-separated):")
            yield Input(value=",".join(self.task.tags), id="tags")
            yield Label("Priority:")
            yield Input(value=str(self.task.priority or ""), id="priority")
            yield Label("Flagged:")
            yield Switch(value=self.task.is_flagged, id="flagged")
            yield Button("Save", variant="primary", id="save")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.task.description = self.query_one("#description", Input).value
            self.task.tags = [tag.strip() for tag in self.query_one("#tags", Input).value.split(",")]
            priority_str = self.query_one("#priority", Input).value
            try:
                self.task.priority = int(priority_str) if priority_str else None
            except ValueError:
                self.app.notify("Invalid priority. Please enter a number.", title="Error", severity="error")
                return
            self.task.is_flagged = self.query_one("#flagged", Switch).value
            self.dismiss(self.task)
        else:
            self.dismiss()