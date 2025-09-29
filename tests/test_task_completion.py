import pytest
from unittest.mock import AsyncMock, MagicMock

from textual.pilot import Pilot

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.mark.asyncio
async def test_complete_task(app: LazyTaskApp, mock_task_manager: MockTaskManager, monkeypatch):
    """Test that completing a task works correctly."""
    monkeypatch.setattr(mock_task_manager, "get_lists", AsyncMock(return_value=["develop", "develop2"]))
    monkeypatch.setattr(mock_task_manager, "get_tasks", AsyncMock(side_effect=[
        [Task(id="1", title="task 1")],  # Initial tasks
        [],  # Tasks after completion
        [Task(id="1", title="task 1", completed=True)],  # Tasks with completed
    ]))
    monkeypatch.setattr(mock_task_manager, "complete_task", AsyncMock(return_value=Task(id="1", title="task 1", completed=True)))

    await app.add_task("task 1")
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        # Initial state: one task
        assert len(pilot.app.query("TaskItem")) == 1

        # Press 'c' to complete the task
        await pilot.press("c")
        await pilot.pause(0.1)

        # The task should be gone
        assert len(pilot.app.query("TaskItem")) == 0

        # Press 'ctrl+c' to show completed tasks
        await pilot.press("ctrl+c")
        await pilot.pause(0.1)

        # The completed task should be visible
        assert len(pilot.app.query("TaskItem")) == 1
        task_item = pilot.app.query_one("TaskItem")
        assert task_item.data.completed is True
