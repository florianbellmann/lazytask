import datetime
from typing import cast

import pytest
from textual.widgets import ListView

from lazytask.domain.task import Task
from lazytask.presentation.app import TaskListItem


@pytest.mark.asyncio
async def test_edit_date_in_all_view(app, mock_task_manager):
    """Test that editing a task's due date in the 'all' view works correctly."""
    # Given
    task_id = "1"
    original_due_date = datetime.date(2025, 1, 1)
    await mock_task_manager.add_task(
        "Test Task", "develop", id=task_id, due_date=original_due_date
    )

    async with app.run_test() as pilot:
        # When
        # Switch to all view
        await pilot.press("1")
        await pilot.pause()

        # Select the task
        tasks_list = app.query_one(ListView)
        tasks_list.index = 0
        await pilot.pause()

        # Press "d" to edit the date
        await pilot.press("d")
        await pilot.pause()

        # In the date picker, change the date and select it
        from lazytask.presentation.date_picker_screen import DatePickerScreen

        date_picker_screen = app.screen
        assert isinstance(date_picker_screen, DatePickerScreen)

        # Change the date to tomorrow
        from textual_datepicker import DatePicker

        date_picker = date_picker_screen.query_one(DatePicker)
        import pendulum

        date_picker.date = pendulum.instance(datetime.date(2025, 1, 2))
        await pilot.pause()

        # Click the select button
        await pilot.click("#select_date")
        await pilot.pause()

        # Then
        # Verify the task's due date has been updated in the mock task manager
        updated_task = await mock_task_manager.get_task(task_id, "develop")
        assert updated_task is not None
        assert updated_task.due_date == datetime.date(2025, 1, 2)

        # Verify the UI is updated
        tasks_list = app.query_one(ListView)
        task_item = cast(TaskListItem, tasks_list.children[0])
        assert isinstance(task_item.data, Task)
        assert task_item.data.due_date == datetime.date(2025, 1, 2)
