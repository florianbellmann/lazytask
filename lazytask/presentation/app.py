import datetime
import logging
from contextlib import asynccontextmanager

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, LoadingIndicator
from textual.containers import Container

from lazytask.domain.models import Task
from lazytask.container import container
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.help_screen import HelpScreen
from lazytask.presentation.text_input_modal import TextInputModal

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
        self.get_all_tasks_uc = container.get_task_list_use_case
        self.add_task_uc = container.add_task_use_case
        self.complete_task_uc = container.complete_task_use_case
        self.switch_list_uc = container.get_all_task_lists_use_case # This is not ideal, but we'll fix it later
        self.update_task_uc = container.edit_task_date_use_case # This is not ideal, but we'll fix it later
        self.sort_by = "title"
        self.current_list = "develop"

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
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        if self.LOGGING:
            logging.basicConfig(filename="lazytask.log", level=logging.INFO)
        await self.update_tasks_list()

    async def update_tasks_list(self, filter_query: str = ""):
        """Update the tasks list view."""
        tasks_list_view = self.query_one(ListView)
        tasks_list_view.clear()
        async with self.show_loading():
            try:
                task_list = await self.get_all_tasks_uc.execute(self.current_list)
                tasks = task_list.tasks if task_list else []
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
            if task.flagged:
                details.append("flagged")
            details_str = f" ({', '.join(details)})" if details else ""

            list_item = ListItem(Label(f"{'[x]' if task.completed else '[ ]'} {task.title}{details_str}"))
            list_item.data = task
            tasks_list_view.append(list_item)
        self.query_one(Header).title = f"LazyTask - {self.current_list}"

    def action_add_task(self) -> None:
        """An action to add a task."""
        def on_submit(title: str):
            if title:
                async def add_task_async():
                    async with self.show_loading():
                        await self.add_task_uc.execute(self.current_list, Task(id=None, title=title))
                        await self.update_tasks_list()
                self.call_later(add_task_async)

        self.push_screen(TextInputModal(prompt="New task title:"), on_submit)

    def action_switch_list(self) -> None:
        """An action to switch list."""
        def on_submit(list_name: str):
            if list_name:
                self.current_list = list_name
                self.call_later(self.update_tasks_list)

        self.push_screen(TextInputModal(prompt="Switch to list:"), on_submit)

    def action_edit_date(self) -> None:
        """An action to edit a task's due date."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            def on_submit(date_str: str):
                if date_str:
                    try:
                        new_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        task.due_date = new_date
                        async def update_task_async():
                            async with self.show_loading():
                                await self.update_task_uc.execute(self.current_list, task)
                                await self.update_tasks_list()
                        self.call_later(update_task_async)
                    except ValueError:
                        self.notify("Invalid date format. Please use YYYY-MM-DD.", title="Error", severity="error")

            initial_value = task.due_date.strftime('%Y-%m-%d') if task.due_date else ""
            self.push_screen(TextInputModal(prompt="New due date (YYYY-MM-DD):", initial_value=initial_value), on_submit)

    async def action_move_to_tomorrow(self) -> None:
        """An action to move a task to tomorrow."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task = tasks_list.highlighted_child.data
            task.due_date = datetime.date.today() + datetime.timedelta(days=1)
            async with self.show_loading():
                await self.update_task_uc.execute(self.current_list, task)
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
                await self.update_task_uc.execute(self.current_list, task)
                await self.update_tasks_list()

    async def action_refresh(self) -> None:
        """An action to refresh the list."""
        await self.update_tasks_list()

    def action_filter_tasks(self) -> None:
        """An action to filter tasks."""
        def on_submit(query: str):
            self.call_later(self.update_tasks_list, query)

        self.push_screen(TextInputModal(prompt="Filter tasks:"), on_submit)

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
                    await self.complete_task_uc.execute(self.current_list, task.id)
                    await self.update_tasks_list()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = LazyTaskApp()
    app.run()