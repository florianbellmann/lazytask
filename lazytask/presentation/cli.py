from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static
from textual.containers import Container, VerticalScroll
from textual.reactive import var

from lazytask.container import container
from lazytask.domain.models import Task

class TaskDisplay(Static):
    """A widget to display a single task."""
    def __init__(self, task: Task, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.update_content()

    def update_content(self):
        status = "[x]" if self.task.completed else "[ ]"
        title = self.task.title
        description = f"\n  [dim]{self.task.description}[/dim]" if self.task.description else ""
        due_date = f"\n  [dim]Due: {self.task.due_date.strftime('%Y-%m-%d')}[/dim]" if self.task.due_date else ""
        tags = f"\n  [dim]Tags: {', '.join(self.task.tags)}[/dim]" if self.task.tags else ""
        priority = f"\n  [dim]Prio: {self.task.priority}[/dim]" if self.task.priority else ""
        flagged = f"\n  [dim]Flagged: {self.task.flagged}[/dim]" if self.task.flagged else ""

        self.update(f"{status} {title}{description}{due_date}{tags}{priority}{flagged}")

class LazyTaskApp(App):
    """A Textual app for managing tasks."""

    BINDINGS = [
        ("a", "add_task_prompt", "Add Task"),
        ("c", "complete_task_prompt", "Complete Task"),
        ("s", "switch_list_prompt", "Switch List"),
        ("r", "refresh_list", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    current_list_name = var("develop")

    def watch_current_list_name(self, new_name: str) -> None:
        self.update_task_list_display()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with VerticalScroll(id="task-list-container"):
                yield Static("Loading tasks...", id="task-list-display")
            with Container(id="input-container"):
                yield Input(placeholder="Enter task title to add", id="task-input")
                yield Button("Add Task", id="add-task-button", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.update_task_list_display()

    def update_task_list_display(self) -> None:
        task_list = container.get_task_list_use_case.execute(self.current_list_name)
        task_list_display = self.query_one("#task-list-display", Static)
        if task_list:
            content = f"[b]Tasks in '{self.current_list_name}'[/b]\n\n"
            for task in task_list.tasks:
                content += f"[dim]{task.id[:8]}[/dim] - "
                status = "[green]✓[/green]" if task.completed else "[red]✗[/red]"
                content += f"{status} {task.title}\n"
            task_list_display.update(content)
        else:
            task_list_display.update(f"No tasks found in list '{self.current_list_name}'.")

    def action_add_task_prompt(self) -> None:
        self.query_one("#task-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-task-button":
            self.action_add_task()

    def action_add_task(self) -> None:
        input_widget = self.query_one("#task-input", Input)
        title = input_widget.value.strip()
        if title:
            try:
                container.add_task_use_case.execute(self.current_list_name, title)
                input_widget.value = ""
                self.update_task_list_display()
                self.notify(f"Task '{title}' added.")
            except ValueError as e:
                self.notify(str(e), severity="error")
        else:
            self.notify("Task title cannot be empty.", severity="warning")

    def action_complete_task_prompt(self) -> None:
        self.notify("Enter task ID to complete.")
        # For now, just a notification. Later, a modal input.

    def action_switch_list_prompt(self) -> None:
        self.notify("Enter list name to switch to.")
        # For now, just a notification. Later, a modal input.

    def action_refresh_list(self) -> None:
        self.update_task_list_display()
        self.notify(f"List '{self.current_list_name}' refreshed.")

    def action_quit(self) -> None:
        self.exit()

if __name__ == "__main__":
    app = LazyTaskApp()
    app.run()
