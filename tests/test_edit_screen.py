import datetime

import pytest
from textual.widgets import Input

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.date_picker_screen import DatePickerScreen
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture
def mock_task_manager() -> MockTaskManager:
    return MockTaskManager()


@pytest.fixture
def app(mock_task_manager: MockTaskManager, monkeypatch) -> LazyTaskApp:
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
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


async def test_edit_due_date(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    task = await mock_task_manager.add_task(
        "Test Task", due_date=datetime.date(2025, 1, 1)
    )

    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.press("e")
        await pilot.pause(1.0)
        edit_screen = app.screen
        assert isinstance(edit_screen, EditScreen)

        # Check that the initial due date is displayed correctly
        assert str(task.due_date) in edit_screen.get_due_date_label_text()

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
        assert str(new_date) in edit_screen.get_due_date_label_text()

        # Click the "Save" button
        await pilot.click("#save")
        await pilot.pause()

        # Check that the task was updated in the task manager
        updated_task = await mock_task_manager.get_task(task.id)
        assert updated_task is not None
        assert updated_task.due_date == new_date
