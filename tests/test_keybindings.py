import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
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
async def test_initial_state(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the initial state of the app."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(ListView).id == "tasks_list"
        assert app.query_one("#task_detail").id == "task_detail"


@pytest.mark.asyncio
async def test_add_task_keybinding(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the 'a' keybinding for adding a task."""
    app = LazyTaskApp()
    app.add_task_uc = MagicMock()
    app.add_task_uc.execute = AsyncMock()
    app.get_tasks_uc.execute = AsyncMock(return_value=[Task(id="1", title="Test Task")])

    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("T", "e", "s", "t", " ", "T", "a", "s", "k")
        await pilot.press("enter")
        await pilot.pause()

        app.add_task_uc.execute.assert_called_once_with(
            "Test Task", "develop", due_date=None
        )


@pytest.mark.asyncio
async def test_complete_task_keybinding(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the 'c' keybinding for completing a task."""
    app = LazyTaskApp()
    task = Task(id="1", title="Test Task", list_name="develop")
    app.get_tasks_uc.execute = AsyncMock(return_value=[task])
    app.complete_task_uc = MagicMock()
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
async def test_show_help_keybinding(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the '?' keybinding for showing the help screen."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("?")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)
