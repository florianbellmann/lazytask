
import pytest
from unittest.mock import AsyncMock, MagicMock

from textual.pilot import Pilot
from textual.widgets import ListView

from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.help_screen import HelpScreen
from lazytask.domain.task import Task

@pytest.mark.asyncio
async def test_initial_state():
    """Test the initial state of the app."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        assert app.title == "LazyTask - develop"

@pytest.mark.asyncio
async def test_navigation_keybindings():
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

        tasks_list.action_cursor_down()
        await pilot.pause()
        tasks_list.action_cursor_up()
        await pilot.pause()
        assert tasks_list.index == 0

        # Test 'j' for moving down
        await pilot.press("j")
        assert tasks_list.index == 1
        await pilot.press("j")
        assert tasks_list.index == 2

        # Test 'k' for moving up
        await pilot.press("k")
        assert tasks_list.index == 1
        await pilot.press("k")
        assert tasks_list.index == 0

@pytest.mark.asyncio
async def test_add_task_keybinding():
    """Test the 'a' keybinding for adding a task."""
    app = LazyTaskApp()
    app.add_task_uc.execute = AsyncMock()
    app.get_tasks_uc.execute = AsyncMock(return_value=[Task(id="1", title="Test Task")])

    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.press("T", "e", "s", "t", " ", "T", "a", "s", "k")
        await pilot.press("enter")
        await pilot.pause()

        app.add_task_uc.execute.assert_called_once_with("Test Task", "develop")

@pytest.mark.asyncio
async def test_complete_task_keybinding():
    """Test the 'c' keybinding for completing a task."""
    app = LazyTaskApp()
    task = Task(id="1", title="Test Task")
    app.get_tasks_uc.execute = AsyncMock(return_value=[task])
    app.complete_task_uc.execute = AsyncMock()

    async with app.run_test() as pilot:
        await app.update_tasks_list()
        await pilot.pause()

        tasks_list = app.query_one(ListView)
        tasks_list.index = 0
        await pilot.pause()

        await pilot.press("c")
        await pilot.pause()

        app.complete_task_uc.execute.assert_called_once_with("1", "develop")

@pytest.mark.asyncio
async def test_show_help_keybinding():
    """Test the '?' keybinding for showing the help screen."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("?")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)

@pytest.mark.asyncio
async def test_quit_keybinding():
    """Test the 'q' keybinding for quitting the app."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert app.is_running is False
