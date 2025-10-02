import pytest
import datetime
import pendulum
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.date_picker_screen import DatePickerScreen
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from textual_datepicker import DatePicker


@pytest.mark.asyncio
async def test_date_picker_updates_task_date(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that the date picker correctly updates a task's due date."""
    await mock_task_manager.add_task("Test Task", due_date=datetime.date(2023, 1, 1))

    async with app.run_test() as pilot:
        await pilot.pause()

        # App starts on "all" list, select the task
        await pilot.press("j")
        await pilot.pause()

        # Open the date picker screen
        await pilot.press("d")
        await pilot.pause()

        assert isinstance(app.screen, DatePickerScreen)
        date_picker_screen = app.screen

        # Set a new date on the date picker
        new_date = datetime.date(2024, 12, 25)
        date_picker = date_picker_screen.query_one(DatePicker)
        date_picker.date = pendulum.instance(new_date)

        # Click the select button
        await pilot.click("#select_date")

        # Wait for the async task update to complete
        await pilot.pause(0.5)

        # Verify the task's due date is updated
        updated_tasks = await mock_task_manager.get_tasks("develop")
        updated_task = updated_tasks[0]
        assert updated_task.due_date == new_date
