import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.help_screen import HelpScreen
from textual.widgets import ListView


async def test_tab_keybindings_from_config(monkeypatch):
    monkeypatch.setenv(
        "LAZYTASK_LISTS", "list1,list2,list3,list4,list5,list6,list7,list8"
    )
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "list1")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("2")
        await pilot.pause()
        assert app.current_list == "list1"
        await pilot.press("3")
        await pilot.pause()
        assert app.current_list == "list2"
        await pilot.press("4")
        await pilot.pause()
        assert app.current_list == "list3"
        await pilot.press("5")
        await pilot.pause()
        assert app.current_list == "list4"
        await pilot.press("6")
        await pilot.pause()
        assert app.current_list == "list5"
        await pilot.press("7")
        await pilot.pause()
        assert app.current_list == "list6"
        await pilot.press("8")
        await pilot.pause()
        assert app.current_list == "list7"
        await pilot.press("9")
        await pilot.pause()
        assert app.current_list == "list8"


@pytest.mark.asyncio
async def test_initial_state(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    """Test the initial state of the app."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one(ListView).id == "tasks_list"
        assert app.query_one("#task_detail").id == "task_detail"


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


@pytest.mark.asyncio
async def test_add_task_keybinding(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
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

        app.add_task_uc.execute.assert_called_once_with("Test Task", "develop")


@pytest.mark.asyncio
async def test_complete_task_keybinding(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    """Test the 'c' keybinding for completing a task."""
    app = LazyTaskApp()
    task = Task(id="1", title="Test Task")
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
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    """Test the '?' keybinding for showing the help screen."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("?")
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)


@pytest.mark.asyncio
async def test_quit_keybinding(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    """Test the 'q' keybinding for quitting the app."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert app._exit is True
