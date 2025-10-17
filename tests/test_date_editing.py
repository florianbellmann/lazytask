import asyncio
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


@pytest.mark.asyncio
async def test_edit_date_refreshes_list_after_delayed_backend(
    app, mock_task_manager, monkeypatch
):
    """Ensure the list view reflects date changes even when the backend responds later."""
    task_id = "task-42"
    initial_due_date = datetime.date(2025, 1, 1)
    await mock_task_manager.add_task(
        "Async Task", "develop", id=task_id, due_date=initial_due_date
    )

    new_due_date = datetime.date(2025, 1, 5)
    new_task_id = "task-42-updated"

    async def delayed_execute(
        task_id_param: str, updates: dict, list_name: str = "develop"
    ) -> Task:
        await asyncio.sleep(0.05)
        list_bucket = mock_task_manager._tasks.setdefault(list_name, {})
        original_task = list_bucket.pop(task_id_param)
        updated_task = Task(
            id=new_task_id,
            title=original_task.title,
            completed=original_task.completed,
            due_date=updates.get("due_date", original_task.due_date),
            creation_date=original_task.creation_date,
            list_name=list_name,
            description=original_task.description,
            tags=list(original_task.tags),
            priority=original_task.priority,
            is_flagged=original_task.is_flagged,
            recurring=original_task.recurring,
        )
        list_bucket[new_task_id] = updated_task
        return updated_task

    monkeypatch.setattr(app.update_task_uc, "execute", delayed_execute)

    async with app.run_test() as pilot:
        await pilot.press("1")
        await pilot.pause()

        tasks_list = app.query_one(ListView)
        tasks_list.index = 0
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()

        from lazytask.presentation.date_picker_screen import DatePickerScreen

        date_picker_screen = app.screen
        assert isinstance(date_picker_screen, DatePickerScreen)

        from textual_datepicker import DatePicker
        import pendulum

        date_picker = date_picker_screen.query_one(DatePicker)
        date_picker.date = pendulum.instance(new_due_date)
        await pilot.pause()

        await pilot.click("#select_date")
        await pilot.pause(0.2)

        tasks_list = app.query_one(ListView)
        task_item = cast(TaskListItem, tasks_list.children[0])
        assert isinstance(task_item.data, Task)
        assert task_item.data.due_date == new_due_date
        assert task_item.data.id == new_task_id
