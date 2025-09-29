import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from textual.widgets import ListView
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.mark.asyncio
async def test_move_task_to_list(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    """Test that moving a task to another list works."""
    await mock_task_manager.add_task("task 1", list_name="develop")
    await mock_task_manager.add_task("task 2", list_name="develop")
    await mock_task_manager.add_task("task 3", list_name="develop")
    await mock_task_manager.add_task("task 4", list_name="develop2")

    async with app.run_test() as pilot:
        await pilot.pause()

        # Check that we are on the develop list
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 3

        # Move down to the 3rd item (index 2)
        await pilot.press("j")
        await pilot.pause()
        await pilot.press("j")
        await pilot.pause()
        await pilot.press("j")
        await pilot.pause()
        assert list_view.index == 2

        # Press 'y' to open the select list screen
        await pilot.press("y")
        await pilot.pause()

        # Select the second list (develop2)
        await pilot.press("j")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause(1)

        # Check that the task was moved
        develop_tasks = await mock_task_manager.get_tasks("develop")
        develop2_tasks = await mock_task_manager.get_tasks("develop2")
        assert len(develop_tasks) == 2
        assert len(develop2_tasks) == 2
        assert "task 3" in [task.title for task in develop2_tasks]