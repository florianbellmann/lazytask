import asyncio
import datetime
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import cast

from textual.app import App, ComposeResult
from textual import events
from textual.widgets import Header, Footer, ListView, ListItem, Label, LoadingIndicator
from textual.containers import Container, Horizontal
from rich.text import Text

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
from lazytask.presentation.theme import build_theme_css
from lazytask.presentation.palette import get_palette
from .date_picker_screen import DatePickerScreen
from .select_list_screen import SelectListScreen
from .sort_options_screen import SortOptionsScreen
from lazytask.application.errors import DescriptionEditorError
from lazytask.container import container

PALETTE = get_palette()
logger = logging.getLogger(__name__)


class TaskListItem(ListItem):
    def __init__(self, task: Task):
        super().__init__()
        self.data = task
        self.add_class("task-list-item")
        if task.completed:
            self.add_class("completed")
        if task.is_flagged:
            self.add_class("flagged")
        # eliminate extra spacing between items
        self.styles.margin = 0

    def compose(self) -> ComposeResult:
        status_token = "[x]" if self.data.completed else "[ ]"
        meta_parts: list[str] = []
        if self.data.tags:
            meta_parts.append(f"tags: {','.join(self.data.tags)}")
        if self.data.priority:
            meta_parts.append(f"prio: {self.data.priority}")
        if self.data.is_flagged:
            meta_parts.append("flagged")

        status_color = (
            PALETTE.success if self.data.completed else PALETTE.accent_primary
        )
        title_color = (
            PALETTE.text_muted if self.data.completed else PALETTE.text_primary
        )
        meta_color = PALETTE.text_secondary
        due_color = PALETTE.accent_primary

        due_text = Text()
        if self.data.due_date:
            today = datetime.date.today()
            if self.data.completed:
                due_color = PALETTE.success
            elif self.data.due_date < today:
                due_color = PALETTE.danger
            elif self.data.due_date == today:
                due_color = PALETTE.warning
            else:
                due_color = PALETTE.accent_primary
            effective_due_color = due_color
            due_text.append(
                f"due: {self.data.due_date.strftime('%Y-%m-%d')}", style=due_color
            )
        else:
            due_text.append("due: -", style=meta_color)
            effective_due_color = meta_color

        display_text = Text()
        display_text.append(status_token, style=status_color)
        display_text.append(f" {self.data.title}", style=title_color)
        if meta_parts:
            display_text.append(f" ({', '.join(meta_parts)})", style=meta_color)

        title_label = Label(display_text, id="task-title")
        title_label.styles.color = title_color
        title_label.styles.padding = 0

        due_label = Label(due_text, id="task-due-date")
        due_label.styles.color = effective_due_color
        due_label.styles.padding = 0

        logger.debug(
            "TaskListItem compose: title=%s status_color=%s title_color=%s due_color=%s classes=%s tags=%s",
            self.data.title,
            status_color,
            title_color,
            effective_due_color,
            sorted(self.classes),
            self.data.tags,
        )

        yield Horizontal(
            title_label,
            due_label,
            id="task-item-row",
        )


class LazyTaskApp(App):
    """A Textual app to manage tasks."""

    CSS_PATH = None
    CSS = build_theme_css(PALETTE)
    LOGGING = True

    BINDINGS = [
        ("y", "move_task", "Move task"),
        ("d", "edit_date", "Edit date"),
        ("a", "add_task", "Add task"),
        ("A", "add_task_due_today", "Add task due today"),
        ("c", "complete_task", "Complete task"),
        ("r", "edit_title", "Edit title"),
        ("e", "edit_description", "Edit description"),
        ("o", "move_to_tomorrow", "Move to tomorrow"),
        ("t", "due_today", "Due today"),
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
        self.description_editor = container.get_description_editor()
        self.sort_by = "due_date"
        self.sort_reverse = False

        lists_str = os.environ.get("LAZYTASK_LISTS")

        if lists_str is None:
            raise ValueError("LAZYTASK_LISTS environment variable not set")

        if not lists_str.strip():
            raise ValueError("LAZYTASK_LISTS must not be empty")

        self.available_lists = [name.strip() for name in lists_str.split(",")]
        self.current_list = "all"

        self.title = f"LazyTask - {self.current_list}"
        self.show_overdue_only = False
        self.show_completed = False
        self.filter_query = ""

    async def add_task(self, title: str, due_today: bool = False):
        # When viewing "all", add to the first available list
        list_name = (
            self.current_list if self.current_list != "all" else self.available_lists[0]
        )
        due_date = datetime.date.today() if due_today else None
        new_task = await self.add_task_uc.execute(title, list_name, due_date=due_date)
        await self.update_tasks_list(newly_added_task_id=new_task.id)

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
        loading_indicator = LoadingIndicator(id="tasks_loading")
        loading_indicator.display = False
        tasks_list = ListView(id="tasks_list")
        tasks_list.styles.margin = 0
        yield Horizontal(
            Container(
                loading_indicator,
                tasks_list,
                id="tasks_panel",
            ),
            TaskDetail(id="task_detail"),
            id="main_layout",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        if "pytest" in sys.modules:
            logging.basicConfig(
                filename="lazytask.log", level=logging.DEBUG, force=True
            )
            logging.debug("on_mount called")
        elif self.LOGGING:
            logging.basicConfig(filename="lazytask.log", level=logging.INFO)
        if not self.available_lists:
            self.available_lists = await self.get_lists_uc.execute()
        await self.update_tasks_list()
        self.query_one(ListView).index = None
        self.query_one(TaskDetail).update_task(None)

    async def switch_list(self, list_name: str):
        cleaned_list = list_name.strip()
        if not cleaned_list:
            self.notify("List name must not be empty", title="Invalid list")
            return
        self.current_list = cleaned_list
        self.filter_query = ""
        list_view = self.query_one(ListView)
        list_view.index = None
        await self.update_tasks_list(
            preserve_selection=False, select_first_if_available=True
        )

    async def on_key(self, event: events.Key) -> None:
        logging.debug(
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
                "o",
                "r",
            ]
            and self.query_one(ListView).index is None
        ):
            logging.debug("on_key: preventing default")
            event.prevent_default()
            return

        if event.key == "tab":
            logging.debug("on_key: remapping tab to toggle sort direction")
            event.prevent_default()
            asyncio.create_task(self.action_toggle_sort_direction())
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
        select_first_if_available: bool = False,
    ):
        """Update the tasks list view."""
        logging.debug(
            f"update_tasks_list called with show_completed={self.show_completed}"
        )
        if filter_query is not None:
            self.filter_query = filter_query

        self.query_one(ListTabs).update_lists(self.available_lists, self.current_list)
        tasks_list_view = self.query_one(ListView)
        previous_task_id: str | None = None
        previous_index: int | None = None
        if preserve_selection:
            highlighted = tasks_list_view.highlighted_child
            if isinstance(highlighted, TaskListItem):
                previous_task_id = highlighted.data.id
            previous_index = tasks_list_view.index

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

            # Clear the list after fetching data to minimize visible delay
            await tasks_list_view.clear()

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
        elif preserve_selection:
            had_previous_selection = (
                previous_task_id is not None or previous_index is not None
            )
            if previous_task_id:
                for i, item in enumerate(tasks_list_view.children):
                    if cast(TaskListItem, item).data.id == previous_task_id:
                        tasks_list_view.index = i
                        break
                else:
                    if had_previous_selection and tasks_list_view.children:
                        tasks_list_view.index = 0
                    else:
                        tasks_list_view.index = None
            elif previous_index is not None and 0 <= previous_index < len(
                tasks_list_view.children
            ):
                tasks_list_view.index = previous_index
            elif had_previous_selection and tasks_list_view.children:
                tasks_list_view.index = 0
            else:
                tasks_list_view.index = None
        else:
            if select_first_if_available and tasks_list_view.children:
                tasks_list_view.index = 0
            else:
                tasks_list_view.index = None

    def action_add_task(self) -> None:
        """An action to add a task."""

        def on_submit(title: str | None) -> None:
            if title:
                asyncio.create_task(self.add_task(title))

        self.push_screen(TextInputModal(prompt="New task title:"), on_submit)

    def action_add_task_due_today(self) -> None:
        """An action to add a task that is due today."""

        def on_submit(title: str | None) -> None:
            if title:
                asyncio.create_task(self.add_task(title, due_today=True))

        self.push_screen(
            TextInputModal(prompt="New task title (due today):"), on_submit
        )

    def action_switch_list(self) -> None:
        """An action to switch list."""

        def on_submit(list_name: str | None) -> None:
            if list_name:
                cleaned_list = list_name.strip()
                if cleaned_list:
                    asyncio.create_task(self.switch_list(cleaned_list))

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
                        self.update_task_uc.execute(task.id, updates, task.list_name)
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
                await self.update_task_uc.execute(task.id, updates, task.list_name)
                await self.update_tasks_list()

    async def action_due_today(self) -> None:
        """An action to set a task's due date to today."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data
            updates = {"due_date": datetime.date.today()}
            async with self.show_loading():
                await self.update_task_uc.execute(task.id, updates, task.list_name)
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
                await self.update_task_uc.execute(task.id, updates, task.list_name)
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
                await self.update_task_uc.execute(task.id, updates, task.list_name)
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
            EditScreen(task_id=task.id, list_name=task.list_name), on_close
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
                    lists=[
                        list_name
                        for list_name in self.available_lists
                        if list_name != task.list_name
                    ]
                ),
                on_list_selected,
            )

    async def move_task(self, task: Task, to_list: str):
        """Move a task to another list."""
        async with self.show_loading():
            await self.move_task_uc.execute(task.id, task.list_name, to_list)
            await self.update_tasks_list()

    def action_edit_title(self) -> None:
        """An action to edit a task's title."""
        tasks_list = self.query_one(ListView)
        if tasks_list.highlighted_child:
            task: Task = cast(TaskListItem, tasks_list.highlighted_child).data

            def on_submit(new_title: str | None) -> None:
                if new_title is not None:
                    updates = {"title": new_title}

                    async def update_task_async() -> None:
                        async with self.show_loading():
                            await self.update_task_uc.execute(
                                task.id, updates, task.list_name
                            )
                            await self.update_tasks_list()

                    asyncio.create_task(update_task_async())

            self.push_screen(
                TextInputModal(
                    prompt="Edit title:",
                    initial_value=task.title or "",
                ),
                on_submit,
            )

    async def action_edit_description(self) -> None:
        """An action to edit a task's description using an external editor."""
        tasks_list_view = self.query_one(ListView)
        highlighted_item = tasks_list_view.highlighted_child
        if highlighted_item is None:
            return

        selected_task_item = cast(TaskListItem, highlighted_item)
        task: Task = selected_task_item.data
        initial_description = task.description or ""

        try:
            edited_description = await self.description_editor.edit(
                self, initial_description
            )
        except DescriptionEditorError as error:
            logging.exception("Description editor failed")
            self.notify(
                str(error),
                title="Editor Error",
                severity="error",
            )
            return

        if edited_description is None or edited_description == initial_description:
            return

        async with self.show_loading():
            await self.update_task_uc.execute(
                task.id,
                {"description": edited_description},
                task.list_name,
            )
            await self.update_tasks_list()

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

    def action_sort_tasks(self) -> None:
        """Open a modal to choose the sort field and direction."""

        def on_sort_selected(selection: tuple[str, bool] | None) -> None:
            if not selection:
                return
            selected_sort, selected_reverse = selection
            if self.sort_by == selected_sort and self.sort_reverse == selected_reverse:
                return

            self.sort_by = selected_sort
            self.sort_reverse = selected_reverse
            asyncio.create_task(self.update_tasks_list())

        self.push_screen(
            SortOptionsScreen(self.sort_by, self.sort_reverse), on_sort_selected
        )

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
        logging.debug(f"cursor_down: index before: {tasks_list.index}")
        if tasks_list.index is None and tasks_list.children:
            tasks_list.index = 0
        elif (
            tasks_list.index is not None
            and tasks_list.index < len(tasks_list.children) - 1
        ):
            tasks_list.index += 1
        logging.debug(f"cursor_down: index after: {tasks_list.index}")

    def action_cursor_up(self) -> None:
        """Move cursor up in the list."""
        tasks_list = self.query_one(ListView)
        logging.debug(f"cursor_up: index before: {tasks_list.index}")
        if tasks_list.index is None and tasks_list.children:
            tasks_list.index = 0
        elif tasks_list.index is not None and tasks_list.index > 0:
            tasks_list.index -= 1
        logging.debug(f"cursor_up: index after: {tasks_list.index}")

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

            await self.complete_task_uc.execute(task.id, task.list_name)
            await self.update_tasks_list(completed_task_index=current_index)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = LazyTaskApp()
