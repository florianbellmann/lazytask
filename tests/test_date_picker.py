import pytest
from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem
from textual.containers import Container
from textual_datepicker import DatePicker
import datetime

from lazytask.presentation.app import LazyTaskApp
from lazytask.domain.task import Task
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.container import container

class DatePickerTestApp(LazyTaskApp):
    """A test app for the DatePickerScreen."""
    def compose(self) -> ComposeResult:
        yield Container(
            ListView(id="tasks_list"),
        )

@pytest.fixture
def mock_task_manager():
    manager = MockTaskManager()
    container.set_task_manager(manager)
    return manager

@pytest.mark.asyncio
async def test_date_picker_updates_task_date(mock_task_manager):
    """Test that the date picker correctly updates a task's due date."""
    # Add a task to the mock task manager
    await mock_task_manager.add_task("Test Task", "develop")
    tasks = await mock_task_manager.get_tasks("develop")
    task_to_edit = tasks[0]

    async with LazyTaskApp().run_test() as harness:
        app = harness.app
        app.current_list = "develop"
        await app.update_tasks_list()

        # Select the task
        tasks_list = app.query_one(ListView)
        tasks_list.highlighted_child = tasks_list.children[0]

        # Open the date picker screen
        app.action_edit_date()
        await harness.wait_for_screen("DatePickerScreen")

        # Get the date picker widget
        date_picker_screen = app.query_one("DatePickerScreen")
        date_picker = date_picker_screen.query_one(DatePicker)

        # Set a new date
        new_date = datetime.date(2024, 12, 25)
        date_picker.date = new_date

        # Click the select button
        await harness.click("#select_date")

        # Wait for the screen to dismiss and task list to update
        await harness.wait_until_ready()

        # Verify the task's due date is updated
        updated_tasks = await mock_task_manager.get_tasks("develop")
        updated_task = updated_tasks[0]
        assert updated_task.due_date == new_date
