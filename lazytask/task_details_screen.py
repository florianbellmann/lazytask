from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.containers import Container

from lazytask.domain.task import Task

class TaskDetailsScreen(Screen):
    def __init__(self, task: Task):
        self.task = task
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(name=f"Task Details - {self.task.title}")
        yield Container(
            Static(f"Title: {self.task.title}"),
            Static(f"Description: {self.task.description or ''}"),
            Static(f"Priority: {self.task.priority}"),
            Static(f"Tags: {', '.join(self.task.tags)}"),
            Static(f"Due Date: {self.task.due_date.strftime('%Y-%m-%d') if self.task.due_date else ''}"),
            Static(f"Completed: {'Yes' if self.task.completed else 'No'}"),
            Static(f"Flagged: {'Yes' if self.task.flagged else 'No'}"),
            Static(f"Recurring: {self.task.recurring or ''}"),
        )
        yield Footer()
