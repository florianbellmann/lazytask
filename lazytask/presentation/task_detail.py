from textual.widgets import Static
from rich.text import Text
from lazytask.domain.task import Task


class TaskDetail(Static):
    """A widget to display the details of a task."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = Text()

    def update_task(self, task: Task | None) -> None:
        if task:
            details = []
            if task.list_name:
                details.append(f"List: {task.list_name}")
            if task.due_date:
                details.append(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
            if task.creation_date:
                details.append(
                    f"Created Date: {task.creation_date.strftime('%Y-%m-%d')}"
                )
            if task.description:
                details.append(f"Notes: {task.description}")
            if task.tags:
                details.append(f"Tags: {', '.join(task.tags)}")
            if task.priority:
                details.append(f"Priority: {task.priority}")
            if task.is_flagged:
                details.append("Flagged")
            if task.recurring:
                details.append(f"Recurring: {task.recurring}")
            if task.completed:
                details.append("Status: Completed")
            else:
                details.append("Status: Pending")

            details_str = "\n".join(details)
            self.text = Text(f"## {task.title}\n\n{details_str}")
            self.update(self.text)
        else:
            self.text = Text("No task selected")
            self.update(self.text)
