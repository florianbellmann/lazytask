import pytest


from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.mark.asyncio
async def test_complete_task(
    app: LazyTaskApp, mock_task_manager: MockTaskManager, monkeypatch
):
    await mock_task_manager.add_task(
        Task(id="1", title="Test task", list_name="develop")
    )
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        # Initial state: one task
        assert len(pilot.app.query("TaskListItem")) == 1

        # Press 'j' to highlight the task
        await pilot.press("j")

        # Press 'c' to complete the task
        await pilot.press("c")
        await pilot.pause(0.1)

        # The task should be gone
        assert len(pilot.app.query("TaskListItem")) == 0

        # Press 'ctrl+c' to show completed tasks
        await pilot.press("ctrl+c")
        await pilot.pause(0.1)

        # The completed task should be visible
        assert len(pilot.app.query("TaskListItem")) == 1
        task_item = pilot.app.query_one("TaskListItem")
        assert task_item.data.completed is True
