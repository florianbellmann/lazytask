import pytest
from textual.widgets import ListView
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container

from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")


async def test_go_to_top():
    """Test that 'g' moves the cursor to the top of the list."""
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1")
    await task_manager.add_task("task 2")
    await task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")

        # Set the cursor to a position other than the top.
        tasks_list.index = 1
        await pilot.pause(0.1)
        assert tasks_list.index == 1

        # Simulate the user pressing 'g'.
        app.action_go_to_top()
        await pilot.pause(0.1)

        # Assert that the cursor is at the top of the list.
        assert tasks_list.index == 0


async def test_go_to_bottom():
    """Test that 'G' moves the cursor to the bottom of the list."""
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1")
    await task_manager.add_task("task 2")
    await task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")

        # Set the cursor to a position other than the bottom.
        tasks_list.index = 0
        await pilot.pause(0.1)
        assert tasks_list.index == 0

        # Simulate the user pressing 'G'.
        app.action_go_to_bottom()
        await pilot.pause(0.1)

        # Assert that the cursor is at the bottom of the list.
        assert tasks_list.index == 2


@pytest.mark.asyncio
async def test_navigation_keybindings(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    """Test the navigation keybindings 'j' and 'k'."""
    app = LazyTaskApp()
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
        # Test 'j' for moving down
        await pilot.press("j")
        await pilot.pause(1.0)
        assert tasks_list.index == 1

        # Test 'k' for moving up
        await pilot.press("k")
        await pilot.pause(
            0.5
        )  # Give more time for the ListView to update its index and render
        assert tasks_list.index == 0
