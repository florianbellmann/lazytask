from rich.text import Text
from textual.widgets import Static

from lazytask.domain.task import Task
from lazytask.presentation.palette import get_palette

PALETTE = get_palette()


class TaskDetail(Static):
    """A widget to display the details of a task."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = Text()
        self._last_signature: tuple | str | None = None

    def update_task(self, task: Task | None) -> None:
        if task:
            signature = (
                task.id,
                task.title,
                task.list_name,
                task.due_date,
                task.creation_date,
                task.description,
                tuple(task.tags),
                task.priority,
                task.is_flagged,
                task.recurring,
                task.completed,
            )
            if signature == self._last_signature:
                return
            detail_rows: list[tuple[str, str]] = []
            if task.list_name:
                detail_rows.append(("List", task.list_name))
            if task.due_date:
                detail_rows.append(("Due Date", task.due_date.strftime("%Y-%m-%d")))
            if task.creation_date:
                detail_rows.append(
                    ("Created Date", task.creation_date.strftime("%Y-%m-%d"))
                )
            if task.description:
                detail_rows.append(("Notes", task.description))
            if task.tags:
                detail_rows.append(("Tags", ", ".join(task.tags)))
            if task.priority:
                detail_rows.append(("Priority", str(task.priority)))
            if task.is_flagged:
                detail_rows.append(("Flagged", "Yes"))
            if task.recurring:
                detail_rows.append(("Recurring", task.recurring))
            detail_rows.append(
                ("Status", "Completed" if task.completed else "Pending")
            )

            renderable = Text()
            renderable.append_text(
                Text(task.title, style=f"bold {PALETTE.accent_secondary}")
            )
            if detail_rows:
                renderable.append("\n\n")
                for index, (label, value) in enumerate(detail_rows):
                    line = Text.assemble(
                        (f"{label}: ", PALETTE.accent_primary),
                        (value, PALETTE.text_primary),
                    )
                    renderable.append_text(line)
                    if index < len(detail_rows) - 1:
                        renderable.append("\n")
            self.text = renderable
            self.update(self.text)
            self._last_signature = signature
        else:
            if self._last_signature == "NO_TASK":
                return
            self.text = Text("No task selected", style=PALETTE.text_muted)
            self.update(self.text)
            self._last_signature = "NO_TASK"
