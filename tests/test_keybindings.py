import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.help_screen import HelpScreen
from textual.widgets import ListView


async def test_tab_keybindings_from_config(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2,list3,list4,list5")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("1")
        await pilot.pause()
        assert app.current_list == "all"
        await pilot.press("2")
        await pilot.pause()
        assert app.current_list == "develop"
        await pilot.press("3")
        await pilot.pause()
        assert app.current_list == "develop2"
        await pilot.press("4")
        await pilot.pause()
        assert app.current_list == "list3"
        await pilot.press("5")
        await pilot.pause()
        assert app.current_list == "list4"


@pytest.mark.asyncio
async def test_initial_state(app: LazyTaskApp):
    """Test the initial state of the app."""
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(ListView).id == "tasks_list"
        assert app.query_one("#task_detail").id == "task_detail"


@pytest.mark.asyncio
async def test_add_task_keybinding(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test the 'a' keybinding for adding a task."""
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("T", "e", "s", "t", " ", "T", "a", "s", "k")
        await pilot.press("enter")
        await pilot.pause()

        tasks = await mock_task_manager.get_tasks("develop")
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"


@pytest.mark.asyncio
async def test_complete_task_keybinding(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test the 'c' keybinding for completing a task."""
    task = await mock_task_manager.add_task(title="Test Task", list_name="develop")

    async with app.run_test() as pilot:
        await app.update_tasks_list()
        await pilot.pause()

        tasks_list = app.query_one(ListView)
        tasks_list.index = 0
        await pilot.pause()

        await pilot.press("c")
        await pilot.pause()

        completed_task = await mock_task_manager.get_task(task.id, "develop")
        assert completed_task.completed is True


@pytest.mark.asyncio
async def test_show_help_keybinding(app: LazyTaskApp):
    """Test the '?' keybinding for showing the help screen."""
    async with app.run_test() as pilot:
        await pilot.press("?")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)
