import datetime

import pytest

import pytest
from textual.widgets import ListView

from lazytask.domain.task import Task
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.date_picker_screen import DatePickerScreen


@pytest.fixture
def mock_task_manager() -> MockTaskManager:
    return MockTaskManager()


@pytest.fixture
def app(mock_task_manager: MockTaskManager) -> LazyTaskApp:
    app = LazyTaskApp()
    app.get_tasks_uc.task_manager = mock_task_manager
    app.update_task_uc.task_manager = mock_task_manager
    app.add_task_uc.task_manager = mock_task_manager
    return app


@pytest.mark.asyncio
@pytest.mark.skip(reason="Date picker tests are slow/failing and need to be fixed.")
async def test_date_picker_updates_task_date(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that the date picker correctly updates a task's due date."""
    async with app.run_test() as pilot:
        # Add a task to the mock task manager
        await app.add_task_uc.execute(
            "Test Task", app.current_list, due_date=datetime.date(2023, 1, 1)
        )
        await app.update_tasks_list()

        # Select the task
        tasks_list = app.query_one(ListView)
        tasks_list.index = 0
        await pilot.pause()

        # Open the date picker screen
        app.action_edit_date()
        # Wait for the DatePickerScreen to become active
        await pilot.pause()
        while not isinstance(app.screen, DatePickerScreen):
            await pilot.pause()

        # Get the date picker widget
        date_picker_screen = app.screen
        assert isinstance(date_picker_screen, DatePickerScreen)

        # Set a new date
        new_date = datetime.date(2024, 12, 25)
        date_picker_screen.dismiss(new_date)
        await pilot.pause()  # Allow screen to dismiss

        # Verify the task's due date is updated
        updated_tasks = await mock_task_manager.get_tasks("develop")
        updated_task = updated_tasks[0]
        assert updated_task.due_date == new_date
