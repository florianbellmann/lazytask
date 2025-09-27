import pytest
import datetime
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.date_picker_screen import DatePickerScreen
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.mark.asyncio
async def test_date_picker_updates_task_date(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that the date picker correctly updates a task's due date."""
    await mock_task_manager.add_task("Test Task", due_date=datetime.date(2023, 1, 1))

    async with app.run_test() as pilot:
        # Select the task
        await pilot.press("j")
        await pilot.pause()

        # Open the date picker screen
        await pilot.press("d")
        await pilot.pause()

        assert isinstance(app.screen, DatePickerScreen)
        date_picker_screen = app.screen

        # Set a new date
        new_date = datetime.date(2024, 12, 25)
        date_picker_screen.dismiss(new_date)
        await pilot.pause()  # Allow screen to dismiss

        # Verify the task's due date is updated
        updated_tasks = await mock_task_manager.get_tasks("develop")
        updated_task = updated_tasks[0]
        assert updated_task.due_date == new_date
