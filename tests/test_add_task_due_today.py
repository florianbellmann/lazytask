import datetime

import pytest
from textual.widgets import Label

from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.app import LazyTaskApp


@pytest.mark.asyncio
async def test_add_task_due_today(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    async with app.run_test() as pilot:
        await pilot.press("A")
        await pilot.pause(0.1)

        # Enter title in the modal
        await pilot.press("T")
        await pilot.press("e")
        await pilot.press("s")
        await pilot.press("t")
        await pilot.press("enter")
        await pilot.pause(0.1)

        # Check if the task was added with due date today
        tasks = await mock_task_manager.get_tasks("develop")
        assert len(tasks) == 1
        assert tasks[0].title == "Test"
        assert tasks[0].due_date == datetime.date.today()

        # Ensure the UI reflects the due date
        tasks_list = app.query_one("ListView")
        first_item = tasks_list.children[0]
        due_label = first_item.query_one("Label#task-due-date", Label)
        due_text = str(due_label.render())
        assert f"due: {datetime.date.today().strftime('%Y-%m-%d')}" in due_text
