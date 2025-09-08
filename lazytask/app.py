
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, Label, ListView
from textual.containers import Container
from textual.binding import Binding
from textual.worker import work
from datetime import datetime, timedelta
from enum import Enum

from lazytask.domain.backend import Backend
from lazytask.domain.task import Task
from lazytask.infrastructure.mock_backend import MockBackend
from lazytask.task_details_screen import TaskDetailsScreen
from lazytask.edit_task_screen import EditTaskScreen

class SortOption(Enum):
    NONE = 0
    PRIORITY = 1
    DUE_DATE = 2

class TaskItem(ListItem):
    def __init__(self, task: Task):
        super().__init__()
        self.task = task

    def compose(self) -> ComposeResult:
        completed_str = "[X]" if self.task.completed else "[ ]"
        priority_str = f"P{self.task.priority}"
        due_date_str = self.task.due_date.strftime("%Y-%m-%d") if self.task.due_date else ""
        flag_str = " 🚩" if self.task.flagged else ""
        recurring_str = " 🔁" if self.task.recurring else ""

        yield Label(f"{completed_str} {self.task.title} ({priority_str}) {due_date_str}{flag_str}{recurring_str}")

class LazyTaskApp(App):

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("d", "details", "Details"),
        Binding("e", "edit_task", "Edit"),
        Binding("t", "move_to_tomorrow", "Tomorrow"),
        Binding("f", "toggle_flag", "Flag"),
        Binding("o", "toggle_overdue", "Overdue"),
        Binding("s p", "sort_priority", "Sort by Priority"),
        Binding("s d", "sort_due_date", "Sort by Due Date"),
        Binding("s c", "clear_sort", "Clear Sort"),
    ]

    def __init__(self, backend: Backend):
        self.backend = backend
        self.show_overdue_only = False
        self.sort_option = SortOption.NONE
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(name="LazyTask")
        yield Container(
            ListView(id="task_list"),
            Input(placeholder="Add a new task..."),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_tasks()

    @work
    def refresh_tasks(self) -> None:
        task_list = self.query_one(ListView)
        task_list.clear()
        tasks = self.backend.get_all_tasks()
        from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ListItem, Label, ListView
from textual.containers import Container
from textual.binding import Binding
from textual.worker import work
from datetime import datetime, timedelta
from enum import Enum
import logging

from lazytask.domain.backend import Backend
from lazytask.domain.task import Task
from lazytask.infrastructure.mock_backend import MockBackend
from lazytask.task_details_screen import TaskDetailsScreen
from lazytask.edit_task_screen import EditTaskScreen
from lazytask.help_screen import HelpScreen
from lazytask.logging import setup_logging

class SortOption(Enum):
    NONE = 0
    PRIORITY = 1
    DUE_DATE = 2

class TaskItem(ListItem):
    def __init__(self, task: Task):
        super().__init__()
        self.task = task

    def compose(self) -> ComposeResult:
        completed_str = "[X]" if self.task.completed else "[ ]"
        priority_str = f"P{self.task.priority}"
        due_date_str = self.task.due_date.strftime("%Y-%m-%d") if self.task.due_date else ""
        flag_str = " 🚩" if self.task.flagged else ""
        recurring_str = " 🔁" if self.task.recurring else ""

        yield Label(f"{completed_str} {self.task.title} ({priority_str}) {due_date_str}{flag_str}{recurring_str}")

class LazyTaskApp(App):

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("d", "details", "Details"),
        Binding("e", "edit_task", "Edit"),
        Binding("t", "move_to_tomorrow", "Tomorrow"),
        Binding("f", "toggle_flag", "Flag"),
        Binding("o", "toggle_overdue", "Overdue"),
        Binding("s p", "sort_priority", "Sort by Priority"),
        Binding("s d", "sort_due_date", "Sort by Due Date"),
        Binding("s c", "clear_sort", "Clear Sort"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self, backend: Backend):
        self.backend = backend
        self.show_overdue_only = False
        self.sort_option = SortOption.NONE
        setup_logging()
        logging.info("Application started")
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(name="LazyTask")
        yield Container(
            ListView(id="task_list"),
            Input(placeholder="Add a new task..."),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_tasks()

    @work
    def refresh_tasks(self) -> None:
        logging.info("Refreshing tasks")
        task_list = self.query_one(ListView)
        task_list.clear()
        tasks = self.backend.get_all_tasks()
        if self.show_overdue_only:
            tasks = [task for task in tasks if task.due_date and task.due_date < datetime.now() and not task.completed]

        if self.sort_option == SortOption.PRIORITY:
            tasks.sort(key=lambda x: x.priority, reverse=True)
        elif self.sort_option == SortOption.DUE_DATE:
            tasks.sort(key=lambda x: x.due_date if x.due_date else datetime.max)

        for task in tasks:
            item = TaskItem(task)
            task_list.append(item)

    @work
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        logging.info(f"Adding new task: {event.value}")
        self.backend.add_task(event.value)
        self.refresh_tasks()
        self.query_one(Input).value = ""

    @work
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, TaskItem):
            logging.info(f"Completing task: {event.item.task.title}")
            self.backend.complete_task(event.item.task.id)
            self.refresh_tasks()

    def action_refresh(self) -> None:
        self.refresh_tasks()

    def action_details(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            self.push_screen(TaskDetailsScreen(task_list.highlighted_child.task))

    def action_edit_task(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            self.push_screen(EditTaskScreen(task_list.highlighted_child.task))

    @work
    def action_move_to_tomorrow(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            task = task_list.highlighted_child.task
            logging.info(f"Moving task to tomorrow: {task.title}")
            task.due_date = datetime.now() + timedelta(days=1)
            self.update_task(task)

    @work
    def action_toggle_flag(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            task = task_list.highlighted_child.task
            logging.info(f"Toggling flag for task: {task.title}")
            task.flagged = not task.flagged
            self.update_task(task)

    def action_toggle_overdue(self) -> None:
        self.show_overdue_only = not self.show_overdue_only
        logging.info(f"Toggled show overdue only to: {self.show_overdue_only}")
        self.refresh_tasks()

    def action_sort_priority(self) -> None:
        self.sort_option = SortOption.PRIORITY
        logging.info("Sorting by priority")
        self.refresh_tasks()

    def action_sort_due_date(self) -> None:
        self.sort_option = SortOption.DUE_DATE
        logging.info("Sorting by due date")
        self.refresh_tasks()

    def action_clear_sort(self) -> None:
        self.sort_option = SortOption.NONE
        logging.info("Cleared sorting")
        self.refresh_tasks()

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    @work
    def update_task(self, task: Task) -> None:
        logging.info(f"Updating task: {task.title}")
        self.backend.update_task(task)
        self.refresh_tasks()

if __name__ == "__main__":
    app = LazyTaskApp(backend=MockBackend())
    app.run()


    @work
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.backend.add_task(event.value)
        self.refresh_tasks()
        self.query_one(Input).value = ""

    @work
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, TaskItem):
            self.backend.complete_task(event.item.task.id)
            self.refresh_tasks()

    def action_refresh(self) -> None:
        self.refresh_tasks()

    def action_details(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            self.push_screen(TaskDetailsScreen(task_list.highlighted_child.task))

    def action_edit_task(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            self.push_screen(EditTaskScreen(task_list.highlighted_child.task))

    @work
    def action_move_to_tomorrow(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            task = task_list.highlighted_child.task
            task.due_date = datetime.now() + timedelta(days=1)
            self.update_task(task)

    @work
    def action_toggle_flag(self) -> None:
        task_list = self.query_one(ListView)
        if task_list.highlighted_child and isinstance(task_list.highlighted_child, TaskItem):
            task = task_list.highlighted_child.task
            task.flagged = not task.flagged
            self.update_task(task)

    def action_toggle_overdue(self) -> None:
        self.show_overdue_only = not self.show_overdue_only
        self.refresh_tasks()

    def action_sort_priority(self) -> None:
        self.sort_option = SortOption.PRIORITY
        self.refresh_tasks()

    def action_sort_due_date(self) -> None:
        self.sort_option = SortOption.DUE_DATE
        self.refresh_tasks()

    def action_clear_sort(self) -> None:
        self.sort_option = SortOption.NONE
        self.refresh_tasks()

    @work
    def update_task(self, task: Task) -> None:
        self.backend.update_task(task)
        self.refresh_tasks()

if __name__ == "__main__":
    app = LazyTaskApp(backend=MockBackend())
    app.run()
