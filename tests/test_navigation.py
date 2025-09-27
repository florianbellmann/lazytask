import pytest
from textual.widgets import ListView
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from unittest.mock import AsyncMock
from lazytask.domain.task import Task


async def test_go_to_top(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    """Test that 'g' moves the cursor to the top of the list."""
    await mock_task_manager.add_task("task 1")
    await mock_task_manager.add_task("task 2")
    await mock_task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        tasks_list = app.query_one("ListView")

        # Set the cursor to a position other than the top.
        tasks_list.index = 1
        await pilot.pause(0.1)
        assert tasks_list.index == 1

        # Simulate the user pressing 'g'.
        await pilot.press("g")
        await pilot.pause(0.1)

        # Assert that the cursor is at the top of the list.
        assert tasks_list.index == 0


async def test_go_to_bottom(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    """Test that 'G' moves the cursor to the bottom of the list."""
    await mock_task_manager.add_task("task 1")
    await mock_task_manager.add_task("task 2")
    await mock_task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        tasks_list = app.query_one("ListView")

        # Set the cursor to a position other than the bottom.
        tasks_list.index = 0
        await pilot.pause(0.1)
        assert tasks_list.index == 0

        # Simulate the user pressing 'G'.
        await pilot.press("G")
        await pilot.pause(0.1)

        # Assert that the cursor is at the bottom of the list.
        assert tasks_list.index == 2


@pytest.mark.asyncio
async def test_navigation_keybindings(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test the navigation keybindings 'j' and 'k'."""
    tasks = [
        Task(id="1", title="Task 1"),
        Task(id="2", title="Task 2"),
        Task(id="3", title="Task 3"),
    ]
    app.get_tasks_uc.execute = AsyncMock(return_value=tasks)

    async with app.run_test() as pilot:
        await app.update_tasks_list()
        await pilot.pause()

        tasks_list = app.query_one(ListView)
        assert len(tasks_list.children) == 3

        # Focus the ListView
        tasks_list.focus()
        await pilot.pause()

        # Test 'j' for moving down
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 1

        # Test 'k' for moving up
        await pilot.press("k")
        await pilot.pause(
            0.5
        )  # Give more time for the ListView to update its index and render
        assert tasks_list.index == 0
