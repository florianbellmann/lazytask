
import pytest
from textual.testing.driver import Tester
from textual.widgets import ListView

from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.help_screen import HelpScreen


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
    async with app.run_test() as pilot:
        # Add some tasks for navigation
        await app.add_task_uc.execute("Task 1", "develop")
        await app.add_task_uc.execute("Task 2", "develop")
        await app.add_task_uc.execute("Task 3", "develop")
        await app.update_tasks_list()

        tasks_list = app.query_one(ListView)
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
async def test_dark_mode_keybinding():
    """Test the 'd' keybinding for toggling dark mode."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        initial_dark_mode = app.dark
        await pilot.press("d")
        assert app.dark is not initial_dark_mode
        await pilot.press("d")
        assert app.dark is initial_dark_mode


@pytest.mark.asyncio
async def test_add_task_keybinding():
    """Test the 'a' keybinding for adding a task."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.press("T", "e", "s", "t", " ", "T", "a", "s", "k")
        await pilot.press("enter")
        await pilot.pause()
        tasks_list = app.query_one(ListView)
        assert len(tasks_list.children) == 1
        assert tasks_list.children[0].data.title == "Test Task"



import pytest
from textual.widgets import ListView

from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.help_screen import HelpScreen


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
    async with app.run_test() as pilot:
        # Add some tasks for navigation
        await app.add_task_uc.execute("Task 1", "develop")
        await app.add_task_uc.execute("Task 2", "develop")
        await app.add_task_uc.execute("Task 3", "develop")
        await app.update_tasks_list()

        tasks_list = app.query_one(ListView)
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
async def test_dark_mode_keybinding():
    """Test the 'd' keybinding for toggling dark mode."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        initial_dark_mode = app.dark
        await pilot.press("d")
        assert app.dark is not initial_dark_mode
        await pilot.press("d")
        assert app.dark is initial_dark_mode


@pytest.mark.asyncio
async def test_add_task_keybinding():
    """Test the 'a' keybinding for adding a task."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.press("T", "e", "s", "t", " ", "T", "a", "s", "k")
        await pilot.press("enter")
        await pilot.pause()
        tasks_list = app.query_one(ListView)
        assert len(tasks_list.children) == 1
        assert tasks_list.children[0].data.title == "Test Task"


@pytest.mark.asyncio
async def test_complete_task_keybinding():
    """Test the 'c' keybinding for completing a task."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await app.add_task_uc.execute("Test Task", "develop")
        await app.update_tasks_list()

        tasks_list = app.query_one(ListView)
        assert not tasks_list.children[0].data.completed

        await pilot.press("c")
        await pilot.pause()

        assert tasks_list.children[0].data.completed


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
        assert app._exit



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
        assert app._exit
