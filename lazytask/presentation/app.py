import datetime
import logging
from contextlib import asynccontextmanager

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input, LoadingIndicator
from textual.containers import Container

from lazytask.domain.task import Task
from lazytask.infrastructure.reminders_task_repository import RemindersTaskRepository
from lazytask.application.use_cases import GetAllTasks, AddTask, CompleteTask, SwitchList, UpdateTask
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.help_screen import HelpScreen

class LazyTaskApp(App):
    """A Textual app to manage tasks."""

    LOGGING = True

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_task", "Add task"),
        ("c", "complete_task", "Complete task"),
        ("s", "switch_list", "Switch list"),
        ("e", "edit_date", "Edit date"),
        ("t", "move_to_tomorrow", "Move to tomorrow"),
        ("meta+e", "edit_task", "Edit task"),
        ("ctrl+r", "refresh", "Refresh"),
        ("/", "filter_tasks", "Filter tasks"),
        ("ctrl+o", "sort_tasks", "Sort tasks"),
        ("?", "show_help", "Show help"),
        ("j", "cursor_down", "Cursor Down"),
        ("k", "cursor_up", "Cursor Up"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.repo = RemindersTaskRepository()
        self.get_all_tasks_uc = GetAllTasks(self.repo)
        self.add_task_uc = AddTask(self.repo)
        self.complete_task_uc = CompleteTask(self.repo)
        self.switch_list_uc = SwitchList(self.repo)
        self.update_task_uc = UpdateTask(self.repo)
        self.sort_by = "title"

    @asynccontextmanager
    async def show_loading(self):
        self.query_one(LoadingIndicator).display = True
        yield
        self.query_one(LoadingIndicator).display = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            LoadingIndicator(),
            ListView(id="tasks_list"),
            Input(placeholder="New task...", id="new_task_input"),
            Input(placeholder="Switch to list...", id="switch_list_input", classes="hidden"),
            Input(placeholder="YYYY-MM-DD", id="edit_date_input", classes="hidden"),
            Input(placeholder="Filter...", id="filter_input", classes="hidden"),
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        if self.LOGGING:
            logging.basicConfig(filename="lazytask.log", level=logging.INFO)
        await self.update_tasks_list()

    async def update_tasks_list(self, filter_query: str = ""):
        """Update the tasks list view."""
        tasks_list = self.query_one(ListView)
        tasks_list.clear()
        async with self.show_loading():
            try:
                tasks = await self.get_all_tasks_uc.execute()
            except Exception as e:
                self.notify(f"Error getting tasks: {e}", title="Error", severity="error")
                return

        if filter_query:
            tasks = [task for task in tasks if filter_query.lower() in task.title.lower()]

        if self.sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date or datetime.date.max)
        else:
            tasks.sort(key=lambda t: t.title)

        for task in tasks:
            details = []
            if task.due_date:
                details.append(f"due: {task.due_date.strftime('%Y-%m-%d')}")
            if task.tags:
                details.append(f"tags: {','.join(task.tags)}")
            if task.priority:
                details.append(f"prio: {task.priority}")
            if task.is_flagged:
                details.append("flagged")
            details_str = f" ({', '.join(details)})" if details else ""

            list_item = ListItem(Label(f"{'[x]' if task.completed else '[ ]'} {task.title}{details_str}"))
            list_item.data = task
            tasks_list.append(list_item)
        self.query_one(Header).title = f"LazyTask - {self.repo._current_list}"

    async def on_input_changed(self, message: Input.Changed) -> None:
        if message.input.id == "filter_input":
            await self.update_tasks_list(message.value)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Called when the user submits the input."""
        if message.input.id == "new_task_input":
            if message.value:
                async with self.show_loading():
                    await self.add_task_uc.execute(message.value)
                    await self.update_tasks_list()
                message.input.value = ""
        elif message.input.id == "switch_list_input":
            if message.value:
                self.switch_list_uc.execute(message.value)
                await self.update_tasks_list()
                message.input.value = ""
                message.input.add_class("hidden")
                self.query_one("#new_task_input").remove_class("hidden")
        elif message.input.id == "edit_date_input":
            tasks_list = self.query_one(ListView)
            if tasks_list.highlighted_child and message.value:
                task = tasks_list.highlighted_child.data
                try:
                    new_date = datetime.datetime.strptime(message.value, "%Y-%m-%d").date()
                    task.due_date = new_date
                    async with self.show_loading():
                        await self.update_task_uc.execute(task)
                        await self.update_tasks_list()
                except ValueError:
                    self.notify("Invalid date format. Please use YYYY-MM-DD.", title="Error", severity="error")
            message.input.value = ""
            message.input.add_class("hidden")
            self.query_one("#new_task_input").remove_class("hidden")
        elif message.input.id == "filter_input":
            message.input.add_class("hidden")
            self.query_one("#new_task_input").remove_class("hidden")

    def action_add_task(self) -> None:
        """An action to add a task."""
        self.query_one("#new_task_input").focus()

    def action_switch_list(self) -> None:
        """An action to switch list."""
        self.query_one("#switch_list_input").remove_class("hidden")
        self.query_one("#new_task_input").add_class("hidden")
        self.query_one("#switch_list_input").focus()

    def action_edit_date(self) -> None:
        """An action to edit a task's due date."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            edit_input = self.query_one("#edit_date_input")
            edit_input.remove_class("hidden")
            if task.due_date:
                edit_input.value = task.due_date.strftime('%Y-%m-%d')
            self.query_one("#new_task_input").add_class("hidden")
            edit_input.focus()

    async def action_move_to_tomorrow(self) -> None:
        """An action to move a task to tomorrow."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            task.due_date = datetime.date.today() + datetime.timedelta(days=1)
            async with self.show_loading():
                await self.update_task_uc.execute(task)
                await self.update_tasks_list()

    def action_edit_task(self) -> None:
        """An action to edit a task."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            self.push_screen(EditScreen(task), self.on_edit_screen_closed)

    async def on_edit_screen_closed(self, task: Task) -> None:
        if task:
            async with self.show_loading():
                await self.update_task_uc.execute(task)
                await self.update_tasks_list()

    async def action_refresh(self) -> None:
        """An action to refresh the list."""
        await self.update_tasks_list()

    def action_filter_tasks(self) -> None:
        """An action to filter tasks."""
        self.query_one("#filter_input").remove_class("hidden")
        self.query_one("#new_task_input").add_class("hidden")
        self.query_one("#filter_input").focus()

    async def action_sort_tasks(self) -> None:
        """An action to sort tasks."""
        if self.sort_by == "title":
            self.sort_by = "due_date"
        else:
            self.sort_by = "title"
        await self.update_tasks_list()

    def action_show_help(self) -> None:
        """An action to show the help screen."""
        self.push_screen(HelpScreen())

    def action_cursor_down(self) -> None:
        """Move cursor down in the list."""
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in the list."""
        self.query_one(ListView).action_cursor_up()

    async def action_complete_task(self) -> None:
        """An action to complete a task."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            if task:
                async with self.show_loading():
                    await self.complete_task_uc.execute(task.id)
                    await self.update_tasks_list()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = LazyTaskApp()
    app.run()