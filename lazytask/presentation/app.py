import asyncio
import datetime
import logging
import os
from contextlib import asynccontextmanager
from typing import cast

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
    MoveTask,
)
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.help_screen import HelpScreen
from lazytask.presentation.list_tabs import ListTabs
from lazytask.presentation.task_detail import TaskDetail
from lazytask.presentation.text_input_modal import TextInputModal
from .date_picker_screen import DatePickerScreen
from .select_list_screen import SelectListScreen
from lazytask.container import container


class TaskListItem(ListItem):
    def __init__(self, task: Task):
        super().__init__()
        self.data = task

    def compose(self) -> ComposeResult:
        details = []
        if self.data.due_date:
            details.append(f"due: {self.data.due_date.strftime('%Y-%m-%d')}")
        if self.data.tags:
            details.append(f"tags: {','.join(self.data.tags)}")
        if self.data.priority:
            details.append(f"prio: {self.data.priority}")
        if self.data.is_flagged:
            details.append("flagged")
        details_str = f" ({', '.join(details)})" if details else ""

        yield Label(
            f"{'[x]' if self.data.completed else '[ ]'} {self.data.title}{details_str}"
        )


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
        ("y", "move_task", "Move task"),
        ("d", "edit_date", "Edit date"),
        ("a", "add_task", "Add task"),
        ("c", "complete_task", "Complete task"),
        ("e", "edit_description", "Edit description"),
        ("t", "move_to_tomorrow", "Move to tomorrow"),
        ("m", "move_to_next_monday", "Move to next monday"),
        ("w", "move_to_next_weekend", "Move to next weekend"),
        ("ctrl+d", "toggle_overdue", "Toggle Overdue"),
        ("ctrl+c", "toggle_completed", "Toggle Completed"),
        ("ctrl+r", "refresh", "Refresh"),
        ("/", "filter_tasks", "Filter tasks"),
        ("ctrl+o", "sort_tasks", "Sort tasks"),
        ("ctrl+i", "toggle_sort_direction", "Toggle sort direction"),
        ("?", "show_help", "Show help"),
        ("j", "cursor_down", "Cursor Down"),
        ("k", "cursor_up", "Cursor Up"),
        ("g", "go_to_top", "Go to top"),
        ("G", "go_to_bottom", "Go to bottom"),
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
        self.dark = True
        self.add_task_uc = container.get(AddTask)
        self.get_tasks_uc = container.get(GetTasks)
        self.complete_task_uc = container.get(CompleteTask)
        self.update_task_uc = container.get(UpdateTask)
        self.get_lists_uc = container.get(GetLists)
        self.move_task_uc = container.get(MoveTask)
        self.sort_by = "due_date"
        self.sort_reverse = False

        lists_str = os.environ.get("LAZYTASK_LISTS")

        if lists_str is None:
            raise ValueError("LAZYTASK_LISTS environment variable not set")

        if not lists_str.strip():
            raise ValueError("LAZYTASK_LISTS must not be empty")

        self.available_lists = [name.strip() for name in lists_str.split(",")]
        self.current_list = self.available_lists[0]

        self.title = f"LazyTask - {self.current_list}"
        self.show_overdue_only = False
        self.show_completed = False
        self.filter_query = ""

    async def add_task(self, title: str):
        new_task = await self.add_task_uc.execute(title, self.current_list)
        await self.update_tasks_list(newly_added_task_id=new_task.id)
        tasks_list_view = self.query_one(ListView)

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
        if os.environ.get("PYTEST_CURRENT_TEST"):
            print("on_mount called")
            logging.basicConfig(filename="lazytask.log", level=logging.INFO, force=True)
        elif self.LOGGING:
            logging.basicConfig(filename="lazytask.log", level=logging.INFO)
        if not self.available_lists:
            self.available_lists = await self.get_lists_uc.execute()
        await self.update_tasks_list()
        self.query_one(ListView).index = None
        self.query_one(TaskDetail).update_task(None)

    async def switch_list(self, list_name: str):
        self.current_list = list_name
        self.filter_query = ""
        await self.query_one(ListView).clear()
        await self.update_tasks_list(preserve_selection=False)
        if self.query_one(ListView).children:
            self.query_one(ListView).index = 0

    async def on_key(self, event: events.Key) -> None:
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logging.info(
                f"on_key: key: {event.key}, index: {self.query_one(ListView).index}"
            )
        if (
            event.key
            in [
                "c",
                "d",
                "e",
                "t",
                "m",
            ]
            and self.query_one(ListView).index is None
        ):
            if os.environ.get("PYTEST_CURRENT_TEST"):
                logging.info("on_key: preventing default")
            event.prevent_default()
            return

        if event.key.isdigit():
            digit = int(event.key)
            if digit == 1:
                await self.switch_list("all")
            elif 2 <= digit <= 9:
                list_index = digit - 2
                if list_index < len(self.available_lists):
                    await self.switch_list(self.available_lists[list_index])

    def _update_task_detail(self, item: ListItem | None) -> None:
        if isinstance(item, TaskListItem):
            self.query_one(TaskDetail).update_task(item.data)
        else:
            self.query_one(TaskDetail).update_task(None)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Called when a task is highlighted."""
        self._update_task_detail(event.item)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when a task is selected."""
        self._update_task_detail(event.item)

    async def update_tasks_list(
        self,
        filter_query: str | None = None,
        preserve_selection: bool = True,
        newly_added_task_id: str | None = None,
        completed_task_index: int | None = None,
    ):
        """Update the tasks list view."""
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logging.info(
                f"update_tasks_list called with show_completed={self.show_completed}"
            )
        if filter_query is not None:
            self.filter_query = filter_query

        self.query_one(ListTabs).update_lists(self.available_lists, self.current_list)
        tasks_list_view = self.query_one(ListView)
        selected_task_id = None
        if preserve_selection and tasks_list_view.highlighted_child:
            selected_task_id = cast(
                TaskListItem, tasks_list_view.highlighted_child
            ).data.id

        if newly_added_task_id:
            selected_task_id = newly_added_task_id
        tasks_list_view = self.query_one(ListView)
        await tasks_list_view.clear()
        async with self.show_loading():
            try:
                if self.current_list == "all":
                    all_tasks = []
                    lists = self.available_lists
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

        # Re-query ListView here to ensure we have the latest instance
        tasks_list_view = self.query_one(ListView)

        if self.show_overdue_only:
            today = datetime.date.today()
            tasks = [task for task in tasks if task.due_date and task.due_date <= today]

        if self.filter_query:
            tasks = [
                task
                for task in tasks
                if self.filter_query.lower() in task.title.lower()
            ]

        if self.sort_by == "due_date":
            tasks.sort(
                key=lambda t: t.due_date or datetime.date.max, reverse=self.sort_reverse
            )
        elif self.sort_by == "creation_date":
            tasks.sort(
                key=lambda t: t.creation_date or datetime.datetime.max,
                reverse=self.sort_reverse,
            )
        else:
            tasks.sort(key=lambda t: t.title.lower(), reverse=self.sort_reverse)

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
            tasks_list_view.append(list_item)
        self.title = f"LazyTask - {self.current_list}"

        if completed_task_index is not None:
            num_tasks = len(tasks_list_view.children)
            if num_tasks == 0:
                tasks_list_view.index = None
            else:
                new_index = min(completed_task_index, num_tasks - 1)
                tasks_list_view.index = new_index
        elif newly_added_task_id:
            for i, item in enumerate(tasks_list_view.children):
                if cast(TaskListItem, item).data.id == newly_added_task_id:
                    tasks_list_view.index = i
                    break

        else:
            tasks_list_view.index = None

    def action_add_task(self) -> None:
        """An action to add a task."""

        def on_submit(title: str | None) -> None:
            if title:
                asyncio.create_task(self.add_task(title))

        self.push_screen(TextInputModal(prompt="New task title:"), on_submit)

    def action_switch_list(self) -> None:
        """An action to switch list."""

        def on_submit(list_name: str | None) -> None:
            if list_name:
                asyncio.create_task(self.switch_list(list_name))

        self.push_screen(TextInputModal(prompt="Switch to list:"), on_submit)

    def action_edit_date(self) -> None:
        """An action to edit a task's due date."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data

            def on_date_selected(new_date: datetime.date | None) -> None:
                if new_date:
                    updates = {"due_date": new_date}
                    asyncio.create_task(
                        self.update_task_uc.execute(task.id, updates, self.current_list)
                    )
                    asyncio.create_task(self.update_tasks_list())

            self.push_screen(
                DatePickerScreen(initial_date=task.due_date), on_date_selected
            )

    async def action_move_to_tomorrow(self) -> None:
        """An action to move a task to tomorrow."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data
            updates = {"due_date": datetime.date.today() + datetime.timedelta(days=1)}
            async with self.show_loading():
                await self.update_task_uc.execute(task.id, updates, self.current_list)
                await self.update_tasks_list()

    async def action_move_to_next_monday(self) -> None:
        """An action to move a task to next monday."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data
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
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data
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
        if not tasks_list.highlighted_child:
            return

        task: Task = cast(TaskListItem, tasks_list.highlighted_child).data

        def on_close(updated_task: Task | None) -> None:
            if updated_task:
                asyncio.create_task(self.update_tasks_list())

        self.push_screen(
            EditScreen(task_id=task.id, list_name=self.current_list), on_close
        )

    def action_move_task(self) -> None:
        """An action to move a task to another list."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data

            def on_list_selected(list_name: str | None) -> None:
                if list_name:
                    asyncio.create_task(self.move_task(task, list_name))

            self.push_screen(
                SelectListScreen(
                    lists=[l for l in self.available_lists if l != self.current_list]
                ),
                on_list_selected,
            )

    async def move_task(self, task: Task, to_list: str):
        """Move a task to another list."""
        async with self.show_loading():
            await self.move_task_uc.execute(task.id, self.current_list, to_list)
            await self.update_tasks_list()

    def action_edit_description(self) -> None:
        """An action to edit a task's description."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data

            def on_submit(new_description: str | None) -> None:
                if new_description is not None:
                    updates = {"description": new_description}

                    async def update_task_async() -> None:
                        async with self.show_loading():
                            await self.update_task_uc.execute(
                                task.id, updates, self.current_list
                            )
                            await self.update_tasks_list()

                    asyncio.create_task(update_task_async())

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
        await self.update_tasks_list("")

    def action_filter_tasks(self) -> None:
        """An action to filter tasks."""

        def on_submit(value: str | None) -> None:
            async def filter_and_select():
                await self.update_tasks_list(value or "", preserve_selection=False)
                tasks_list_view = self.query_one(ListView)
                if tasks_list_view.children:
                    tasks_list_view.index = 0
                else:
                    tasks_list_view.index = None

            asyncio.create_task(filter_and_select())

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

    async def action_toggle_sort_direction(self) -> None:
        """An action to toggle the sort direction."""
        self.sort_reverse = not self.sort_reverse
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
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logging.info(f"cursor_down: index before: {tasks_list.index}")
        if tasks_list.index is None and tasks_list.children:
            tasks_list.index = 0
        elif (
            tasks_list.index is not None
            and tasks_list.index < len(tasks_list.children) - 1
        ):
            tasks_list.index += 1
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logging.info(f"cursor_down: index after: {tasks_list.index}")

    def action_cursor_up(self) -> None:
        """Move cursor up in the list."""
        tasks_list = self.query_one(ListView)
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logging.info(f"cursor_up: index before: {tasks_list.index}")
        if tasks_list.index is None and tasks_list.children:
            tasks_list.index = 0
        elif tasks_list.index is not None and tasks_list.index > 0:
            tasks_list.index -= 1
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logging.info(f"cursor_up: index after: {tasks_list.index}")

    def action_go_to_top(self) -> None:
        """Go to the top of the list."""
        tasks_list = self.query_one(ListView)
        tasks_list.index = 0

    def action_go_to_bottom(self) -> None:
        """Go to the bottom of the list."""
        tasks_list = self.query_one(ListView)
        tasks_list.index = len(tasks_list.children) - 1

    async def action_complete_task(self) -> None:
        """An action to complete a task."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            current_index = tasks_list.index
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data

            await self.complete_task_uc.execute(task.id, self.current_list)
            await self.update_tasks_list(completed_task_index=current_index)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = LazyTaskApp()
