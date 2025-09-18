import datetime

import pytest
from textual.widgets import Button, ListView

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.date_picker_screen import DatePickerScreen
from lazytask.infrastructure.mock_task_manager import MockTaskManager


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


@pytest.fixture
async def create_task_in_manager(mock_task_manager: MockTaskManager):
    task = await mock_task_manager.add_task(
        "Test Task", due_date=datetime.date(2025, 1, 1)
    )
    return task


async def test_edit_due_date(app: LazyTaskApp, create_task_in_manager: Task):
    async with app.run_test() as pilot:
        await app.update_tasks_list()  # Now call update_tasks_list after app is running
        await pilot.pause()

        # Select the task
        tasks_list = app.query_one(ListView)
        tasks_list.index = 0
        await pilot.pause()

        edit_screen = EditScreen(
            task_id=create_task_in_manager.id, list_name=app.current_list
        )
        await app.push_screen(edit_screen)
        await pilot.pause(1.0)  # Give ample time for the screen to mount and compose

        await pilot.pause()
        # Check that the initial due date is displayed correctly
        due_date_label = edit_screen.query_one("#due-date-label")
        assert str(create_task_in_manager.due_date) in due_date_label.renderable

        # Click the "Edit Due Date" button
        await pilot.click("#edit-due-date")
        await pilot.pause()

        # Check that the DatePickerScreen is displayed
        date_picker_screen = app.screen
        assert isinstance(date_picker_screen, DatePickerScreen)

        # Select a new date (e.g., today)
        new_date = datetime.date.today()
        date_picker_screen.dismiss(new_date)
        await pilot.pause()

        # Check that the due date label on the EditScreen is updated
        assert str(new_date) in due_date_label.renderable

        # Click the "Save" button
        await pilot.click("#save")
        await pilot.pause()

        # Check that the screen was dismissed with the updated task
        assert edit_screen.is_dismissed
        assert edit_screen.dismiss_result.due_date == new_date
