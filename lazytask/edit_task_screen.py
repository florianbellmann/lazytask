from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button
from textual.containers import Container
from datetime import datetime

from lazytask.domain.task import Task

class EditTaskScreen(Screen):
    def __init__(self, task: Task):
        self.task = task
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(name=f"Edit Task - {self.task.title}")
        yield Container(
            Input(value=self.task.title, id="title"),
            Input(value=self.task.description or "", id="description"),
            Input(value=str(self.task.priority), id="priority"),
            Input(value=",".join(self.task.tags), id="tags"),
            Input(value=self.task.due_date.strftime("%Y-%m-%d") if self.task.due_date else "", id="due_date"),
            Input(value=self.task.recurring or "", id="recurring"),
            Button("Save", id="save"),
            Button("Cancel", id="cancel"),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            try:
                title = self.query_one("#title", Input).value
                description = self.query_one("#description", Input).value
                priority = int(self.query_one("#priority", Input).value)
                tags = self.query_one("#tags", Input).value.split(",")
                due_date_str = self.query_one("#due_date", Input).value
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
                recurring = self.query_one("#recurring", Input).value or None

                updated_task = Task(
                    id=self.task.id,
                    title=title,
                    description=description,
                    priority=priority,
                    tags=tags,
                    due_date=due_date,
                    completed=self.task.completed,
                    flagged=self.task.flagged,
                    recurring=recurring,
                )
                self.app.update_task(updated_task)
                self.app.pop_screen()
            except ValueError:
                self.app.notify("Invalid input", severity="error")
        elif event.button.id == "cancel":
            self.app.pop_screen()
