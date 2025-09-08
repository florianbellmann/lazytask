
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input
from textual.containers import Container

from lazytask.domain.task import Task
from lazytask.infrastructure.mock_task_repository import MockTaskRepository
from lazytask.application.use_cases import GetAllTasks, AddTask, CompleteTask

class LazyTaskApp(App):
    """A Textual app to manage tasks."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_task", "Add task"),
        ("c", "complete_task", "Complete task"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.repo = MockTaskRepository()
        self.get_all_tasks_uc = GetAllTasks(self.repo)
        self.add_task_uc = AddTask(self.repo)
        self.complete_task_uc = CompleteTask(self.repo)
        # Add some initial data
        self.add_task_uc.execute("Buy milk")
        self.add_task_uc.execute("Walk the dog")


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(ListView(id="tasks_list"), Input(placeholder="New task..."))
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.update_tasks_list()

    def update_tasks_list(self):
        """Update the tasks list view."""
        tasks_list = self.query_one(ListView)
        tasks_list.clear()
        tasks = self.get_all_tasks_uc.execute()
        for task in tasks:
            list_item = ListItem(Label(f"{'[x]' if task.completed else '[ ]'} {task.title}"))
            list_item.data = task
            tasks_list.append(list_item)

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Called when the user submits the input."""
        if message.value:
            self.add_task_uc.execute(message.value)
            self.update_tasks_list()
            message.input.value = ""

    def action_add_task(self) -> None:
        """An action to add a task."""
        self.query_one(Input).focus()

    def action_complete_task(self) -> None:
        """An action to complete a task."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            if task:
                self.complete_task_uc.execute(task.id)
                self.update_tasks_list()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = LazyTaskApp()
    app.run()
