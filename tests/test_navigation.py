import pytest
from textual.widgets import ListView
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from unittest.mock import AsyncMock
from lazytask.domain.task import Task


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")


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
    await mock_task_manager.add_task("task 1")
    await mock_task_manager.add_task("task 2")
    await mock_task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")
        assert tasks_list.index is None  # Nothing selected initially

        # Press 'j' to select the first item
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 0

        # Press 'j' to move down
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 1

        # Press 'k' to move up
        await pilot.press("k")
        await pilot.pause()
        assert tasks_list.index == 0
