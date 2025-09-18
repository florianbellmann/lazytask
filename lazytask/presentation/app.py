import datetime
import logging
import os
from contextlib import asynccontextmanager

from textual.app import App, ComposeResult
from textual import events
from textual.widgets import Header, Footer, ListView, ListItem, Label, LoadingIndicator
from textual.containers import Container, Horizontal

from lazytask.domain.task import Task
from lazytask.application.use_cases import (
    AddTask,
    GetTasks,
    CompleteTask,
    UpdateTask,
    GetLists,
)
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.help_screen import HelpScreen
from lazytask.presentation.list_tabs import ListTabs
from lazytask.presentation.task_detail import TaskDetail
from lazytask.presentation.text_input_modal import TextInputModal
from .date_picker_screen import DatePickerScreen
from lazytask.container import container


class TaskListItem(ListItem):
    def __init__(self, task: Task) -> None:
        super().__init__()
        self._task = task


class LazyTaskApp(App):
    """A Textual app to manage tasks."""

    DEFAULT_CSS = """
    #tasks_list {
        width: 50%;
    }
    #task_detail {
        width: 50%;
    }
    """

    LOGGING = True

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_task", "Add task"),
        ("c", "complete_task", "Complete task"),
        ("s", "switch_list", "Switch list"),
        ("e", "edit_date", "Edit date"),
        ("t", "move_to_tomorrow", "Move to tomorrow"),
        ("m", "move_to_next_monday", "Move to next monday"),
        ("w", "move_to_next_weekend", "Move to next weekend"),
        ("meta+e", "edit_task", "Edit task"),
        ("ctrl+d", "toggle_overdue", "Toggle Overdue"),
        ("ctrl+c", "toggle_completed", "Toggle Completed"),
        ("ctrl+r", "refresh", "Refresh"),
        ("/", "filter_tasks", "Filter tasks"),
        ("ctrl+o", "sort_tasks", "Sort tasks"),
        ("?", "show_help", "Show help"),
        ("j", "cursor_down", "Cursor Down"),
        ("k", "cursor_up", "Cursor Up"),
        ("g", "go_to_top", "Go to top"),
        ("G", "go_to_bottom", "Go to bottom"),
        ("ctrl+b", "edit_description", "Edit description"),
        ("escape", "clear_filter", "Clear filter"),
        ("q", "quit", "Quit"),
        ("1", "show_all_tasks", "All Tasks"),
        ("2", "switch_to_list_2", "List 2"),
        ("3", "switch_to_list_3", "List 3"),
        ("4", "switch_to_list_4", "List 4"),
        ("5", "switch_to_list_5", "List 5"),
    ]

    def __init__(self):
        super().__init__()
        self.add_task_uc = container.get(AddTask)
        self.get_tasks_uc = container.get(GetTasks)
        self.complete_task_uc = container.get(CompleteTask)
        self.update_task_uc = container.get(UpdateTask)
        self.get_lists_uc = container.get(GetLists)
        self.sort_by = "due_date"
        self.current_list = os.environ.get("LAZYTASK_DEFAULT_LIST", "develop")
        self.title = f"LazyTask - {self.current_list}"
        self.available_lists = []
        self.show_overdue_only = False
        self.show_completed = False
        self.task_selected = False
        self.context_sensitive_actions = [
            "c",
            "e",
            "t",
            "m",
            "w",
            "meta+e",
        ]

    async def add_task(self, title: str):
        await self.add_task_uc.execute(title, self.current_list)
        await self.update_tasks_list()

    async def clear_tasks(self):
        await self.get_tasks_uc.task_manager.clear_tasks()

    @asynccontextmanager
    async def show_loading(self):
        self.query_one(LoadingIndicator).display = True
        yield
        self.query_one(LoadingIndicator).display = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield ListTabs()
        yield Horizontal(
            Container(
                LoadingIndicator(),
                ListView(id="tasks_list"),
            ),
            TaskDetail(id="task_detail"),
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        if self.LOGGING:
            logging.basicConfig(filename="lazytask.log", level=logging.INFO)
        self.available_lists = await self.get_lists_uc.execute()
        await self.update_tasks_list()
        self.query_one(TaskDetail).update_task(None)

    async def on_key(self, event: events.Key) -> None:
        if event.key in self.context_sensitive_actions and not self.task_selected:
            return

        if event.key.isdigit():
            digit = int(event.key)
            if digit == 1:
                self.current_list = "all"
                await self.update_tasks_list()
            elif 2 <= digit <= 9:
                list_index = digit - 2
                if list_index < len(self.available_lists):
                    self.current_list = self.available_lists[list_index]
                    await self.update_tasks_list()

    async def on_list_view_selected(self, item: TaskListItem):
        """Called when a task is selected."""
        logging.info(f"Selected item data: {item._task}")
        task: Task = item._task
        self.task_selected = item._task is not None
        self.query_one(TaskDetail).update_task(task)

    async def update_tasks_list(self, filter_query: str = ""):
        """Update the tasks list view."""
        self.query_one(ListTabs).update_lists(self.available_lists, self.current_list)
        tasks_list_view = self.query_one(ListView)
        tasks_list_view.clear()
        async with self.show_loading():
            try:
                if self.current_list == "all":
                    all_tasks = []
                    lists = await self.get_lists_uc.execute()
                    for list_name in lists:
                        tasks_in_list = await self.get_tasks_uc.execute(
                            list_name, include_completed=self.show_completed
                        )
                        all_tasks.extend(tasks_in_list)
                    tasks = all_tasks
                else:
                    tasks = await self.get_tasks_uc.execute(
                        self.current_list, include_completed=self.show_completed
                    )
            except Exception as e:
                self.notify(
                    f"Error getting tasks: {e}", title="Error", severity="error"
                )
                return

        if self.show_overdue_only:
            today = datetime.date.today()
            tasks = [task for task in tasks if task.due_date and task.due_date <= today]

        if filter_query:
            tasks = [
                task for task in tasks if filter_query.lower() in task.title.lower()
            ]

        if self.sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date or datetime.date.max)
        elif self.sort_by == "creation_date":
            tasks.sort(key=lambda t: t.creation_date or datetime.datetime.max)
        else:
            tasks.sort(key=lambda t: t.title.lower())

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

            list_item = TaskListItem(task)
            list_item.append(
                Label(f"{'[x]' if task.completed else '[ ]'} {task.title}{details_str}")
            )
            tasks_list_view.append(list_item)
        self.title = f"LazyTask - {self.current_list}"

    def action_add_task(self) -> None:
        """An action to add a task."""

        def on_submit(title: str | None) -> None:
            if title:
                self.call_later(self.add_task, title)

        self.push_screen(TextInputModal(prompt="New task title:"), on_submit)

    def action_switch_list(self) -> None:
        """An action to switch list."""

        def on_submit(list_name: str | None) -> None:
            if list_name:
                self.current_list = list_name
                self.call_later(self.update_tasks_list)

        self.push_screen(TextInputModal(prompt="Switch to list:"), on_submit)

    def action_edit_date(self) -> None:
        """An action to edit a task's due date."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = tasks_list.highlighted_child._task

            def on_date_selected(new_date: datetime.date | None) -> None:
                if new_date:
                    updates = {"due_date": new_date}

                    async def update_task_async() -> None:
                        async with self.show_loading():
                            await self.update_task_uc.execute(
                                task.id, updates, self.current_list
                            )
                            await self.update_tasks_list()

                    self.call_later(update_task_async)

            self.push_screen(
                DatePickerScreen(initial_date=task.due_date), on_date_selected
            )

    async def action_move_to_tomorrow(self) -> None:
        """An action to move a task to tomorrow."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = tasks_list.highlighted_child._task
            updates = {"due_date": datetime.date.today() + datetime.timedelta(days=1)}
            async with self.show_loading():
                await self.update_task_uc.execute(task.id, updates, self.current_list)
                await self.update_tasks_list()

    async def action_move_to_next_monday(self) -> None:
        """An action to move a task to next monday."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = tasks_list.highlighted_child._task
            today = datetime.date.today()
            days_until_monday = (0 - today.weekday() + 7) % 7
            if days_until_monday == 0:  # if today is monday, move to next monday
                days_until_monday = 7
            next_monday = today + datetime.timedelta(days=days_until_monday)
            updates = {"due_date": next_monday}
            async with self.show_loading():
                await self.update_task_uc.execute(task.id, updates, self.current_list)
                await self.update_tasks_list()

    async def action_move_to_next_weekend(self) -> None:
        """An action to move a task to next weekend."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = tasks_list.highlighted_child._task
            today = datetime.date.today()
            days_until_saturday = (5 - today.weekday() + 7) % 7
            if days_until_saturday == 0:  # if today is saturday, move to next saturday
                days_until_saturday = 7
            next_saturday = today + datetime.timedelta(days=days_until_saturday)
            updates = {"due_date": next_saturday}
            async with self.show_loading():
                await self.update_task_uc.execute(task.id, updates, self.current_list)
                await self.update_tasks_list()

    def action_edit_task(self) -> None:
        """An action to edit a task."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = tasks_list.highlighted_child._task
            self.push_screen(EditScreen(task_id=task.id, list_name=self.current_list), self.on_edit_screen_closed)

    async def on_edit_screen_closed(self, task: Task) -> None:
        if task:
            updates = task.__dict__
            async with self.show_loading():
                await self.update_task_uc.execute(task.id, updates, self.current_list)
                await self.update_tasks_list()

    def action_edit_description(self) -> None:
        """An action to edit a task's description."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = tasks_list.highlighted_child._task

            def on_submit(new_description: str | None) -> None:
                if new_description is not None:
                    updates = {"description": new_description}

                    async def update_task_async() -> None:
                        async with self.show_loading():
                            await self.update_task_uc.execute(
                                task.id, updates, self.current_list
                            )
                            await self.update_tasks_list()

                    self.call_later(update_task_async)

            self.push_screen(
                TextInputModal(
                    prompt="Edit description:", initial_value=task.description or ""
                ),
                on_submit,
            )

    async def action_refresh(self) -> None:
        """An action to refresh the list."""
        await self.update_tasks_list()

    async def action_clear_filter(self) -> None:
        """An action to clear the filter."""
        await self.update_tasks_list()

    def action_filter_tasks(self) -> None:
        """An action to filter tasks."""

        def on_submit(value: str | None) -> None:
            self.call_later(self.update_tasks_list, value or "")

        self.push_screen(TextInputModal(prompt="Filter tasks:"), on_submit)

    async def action_sort_tasks(self) -> None:
        """An action to sort tasks."""
        if self.sort_by == "due_date":
            self.sort_by = "title"
        elif self.sort_by == "title":
            self.sort_by = "creation_date"
        else:
            self.sort_by = "due_date"
        await self.update_tasks_list()

    async def action_toggle_overdue(self) -> None:
        """Toggle showing only overdue tasks."""
        self.show_overdue_only = not self.show_overdue_only
        await self.update_tasks_list()

    async def action_toggle_completed(self) -> None:
        """Toggle showing completed tasks."""
        self.show_completed = not self.show_completed
        await self.update_tasks_list()

    def action_show_help(self) -> None:
        """An action to show the help screen."""
        self.push_screen(HelpScreen())

    def action_cursor_down(self) -> None:
        """Move cursor down in the list."""
        tasks_list = self.query_one(ListView)
        tasks_list.action_cursor_down()
        if tasks_list.highlighted_child:
            self.query_one(TaskDetail).update_task(tasks_list.highlighted_child._task)

    def action_cursor_up(self) -> None:
        """Move cursor up in the list."""
        tasks_list = self.query_one(ListView)
        tasks_list.action_cursor_up()
        if tasks_list.highlighted_child:
            self.query_one(TaskDetail).update_task(tasks_list.highlighted_child.task)

    def action_go_to_top(self) -> None:
        """Go to the top of the list."""
        tasks_list = self.query_one(ListView)
        tasks_list.scroll_home(animate=False)
        tasks_list.index = 0
        if tasks_list.highlighted_child:
            self.query_one(TaskDetail).update_task(tasks_list.highlighted_child.task)

    def action_go_to_bottom(self) -> None:
        """Go to the bottom of the list."""
        tasks_list = self.query_one(ListView)
        tasks_list.scroll_end(animate=False)
        tasks_list.index = len(tasks_list.children) - 1
        if tasks_list.highlighted_child:
            self.query_one(TaskDetail).update_task(tasks_list.highlighted_child.task)

    async def action_complete_task(self) -> None:
        """An action to complete a task."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            current_index = tasks_list.index
            task = tasks_list.highlighted_child.task
            if task:
                async with self.show_loading():
                    await self.complete_task_uc.execute(task.id, self.current_list)
                    await self.update_tasks_list()
                    new_list_size = len(tasks_list.children)
                    if new_list_size > 0 and current_index is not None:
                        tasks_list.index = min(current_index, new_list_size - 1)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.app.dark = not self.app.dark


if __name__ == "__main__":
    app = LazyTaskApp()
    app.run()
