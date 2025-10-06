import asyncio
import datetime

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Switch, TextArea
from textual.containers import Vertical

from lazytask.domain.task import Task
from lazytask.presentation.date_picker_screen import DatePickerScreen
from lazytask.container import container
from lazytask.application.use_cases import GetTasks, UpdateTask


class EditScreen(ModalScreen[None]):
    """Screen to edit a task."""

    def __init__(
        self,
        task_id: str,
        list_name: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._task_id = task_id
        self._list_name = list_name
        self._task: Task | None = None
        self.get_tasks_uc = container.get(GetTasks)
        self.update_task_uc = container.get(UpdateTask)

    def on_mount(self) -> None:
        asyncio.create_task(self.load_task())
        self.query_one("#description").focus()

    async def load_task(self) -> None:
        tasks = await self.get_tasks_uc.execute(self._list_name, include_completed=True)
        self._task = next((t for t in tasks if t.id == self._task_id), None)
        if not self._task:
            self.app.notify(
                f"Task with ID {self._task_id} not found.",
                title="Error",
                severity="error",
            )
            self.dismiss()
            return
        self.query_one("#description", TextArea).text = self._task.description or ""
        self.query_one("#tags", Input).value = ",".join(self._task.tags)
        self.query_one("#priority", Input).value = str(self._task.priority or "")
        self.query_one("#flagged", Switch).value = self._task.is_flagged
        self.query_one("#due-date-label", Label).update(
            str(self._task.due_date) if self._task.due_date else "No due date"
        )

    def compose(self) -> ComposeResult:
        with Vertical(id="edit-task-dialog") as container:
            container.border_title = "Edit Task"
            yield Label("Description:")
            yield TextArea(
                text="", id="description"
            )  # Initial empty value, will be updated in on_mount
            yield Label("Tags (comma-separated):")
            yield Input(
                value="", id="tags"
            )  # Initial empty value, will be updated in on_mount
            yield Label("Priority:")
            yield Input(
                value="", id="priority"
            )  # Initial empty value, will be updated in on_mount
            yield Label("Flagged:")
            yield Switch(
                value=False, id="flagged"
            )  # Initial empty value, will be updated in on_mount
            yield Label("Due Date:")
            yield Label(
                "No due date", id="due-date-label"
            )  # Initial empty value, will be updated in on_mount
            yield Button("Edit Due Date", id="edit-due-date")
            yield Button("Save", variant="primary", id="save")
            yield Button("Cancel", id="cancel")

    def get_due_date_label_text(self) -> str:
        return str(self.query_one("#due-date-label").render())

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if not self._task:
            self.dismiss()
            return

        if event.button.id == "save":
            priority_str = self.query_one("#priority", Input).value
            priority = int(priority_str) if priority_str else None
            updates = {
                "description": self.query_one("#description", TextArea).text,
                "tags": [
                    tag.strip()
                    for tag in self.query_one("#tags", Input).value.split(",")
                ],
                "priority": priority,
                "is_flagged": self.query_one("#flagged", Switch).value,
                "due_date": self._task.due_date,
            }
            priority_str = self.query_one("#priority", Input).value
            if priority_str:
                try:
                    updates["priority"] = int(priority_str)
                except ValueError:
                    self.app.notify(
                        "Invalid priority. Please enter a number.",
                        title="Error",
                        severity="error",
                    )
                    return

            updated_task = await self.update_task_uc.execute(
                self._task.id, updates, self._list_name
            )
            self.dismiss(updated_task)

        elif event.button.id == "edit-due-date":

            def on_date_selected(new_date: datetime.date | None) -> None:
                if self._task:
                    self._task.due_date = new_date
                    self.query_one("#due-date-label", Label).update(
                        str(new_date) if new_date else "No due date"
                    )

            self.app.push_screen(
                DatePickerScreen(initial_date=self._task.due_date), on_date_selected
            )
        else:
            self.dismiss()
