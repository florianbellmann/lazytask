import datetime

import pytest

from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.app import LazyTaskApp


@pytest.mark.asyncio
async def test_due_today_hotkey(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    # Add a task without a due date
    await mock_task_manager.add_task(title="Test task", list_name="develop")

    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        # Initial state: one task
        assert len(pilot.app.query("TaskListItem")) == 1
        task_item = pilot.app.query_one("TaskListItem")
        assert task_item.data.due_date is None

        # Press 'j' to highlight the task
        await pilot.press("j")

        # Press 't' to set due date to today
        await pilot.press("t")
        await pilot.pause(0.1)

        # The task should have today as due date
        task_item = pilot.app.query_one("TaskListItem")
        assert task_item.data.due_date == datetime.date.today()
