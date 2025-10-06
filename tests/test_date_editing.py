import asyncio
import datetime
import os
from typing import cast

import pytest
from textual.widgets import ListView

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp, TaskListItem
from lazytask.domain.task_manager import TaskManager

# Set the LAZYTASK_LISTS environment variable for the tests
os.environ["LAZYTASK_LISTS"] = "develop,develop2"


@pytest.mark.asyncio
async def test_edit_date_in_all_view(mock_task_manager):
    """Test that editing a task's due date in the 'all' view works correctly."""
    # Given
    app = LazyTaskApp(task_manager=mock_task_manager)
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

        # In the date picker, select a new date (e.g., by pressing enter on the default)
        await pilot.press("enter")
        await pilot.pause()

        # Then
        # Verify the task's due date has been updated in the mock task manager
        updated_task = await mock_task_manager.get_task(task_id, "develop")
        assert updated_task is not None
        assert updated_task.due_date != original_due_date

        # Verify the UI is updated
        tasks_list = app.query_one(ListView)
        task_item = cast(TaskListItem, tasks_list.children[0])
        assert isinstance(task_item.data, Task)
        assert task_item.data.due_date == updated_task.due_date
