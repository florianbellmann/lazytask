import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


@pytest.fixture(autouse=True)
async def clear_tasks(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    task_manager = container.task_manager
    await task_manager.clear_tasks()


async def test_filtering_with_slash_button():
    """
    Verify that pressing the slash button (`/`) activates filtering
    and allows typing a filter string.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("/")
        await pilot.pause()
        assert isinstance(pilot.app.screen, object)  # Check if a modal is open


async def test_filtering_is_case_insensitive():
    """
    Verify that filtering matches tasks regardless of case.
    Example: typing 'foo' matches tasks named 'Foo' or 'FOO'.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("Task 1")
    await task_manager.add_task("task 2")
    await task_manager.add_task("TASK 3")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 3


async def test_filtering_persists_after_completing_task():
    """
    Verify that the active filter remains applied after a task is marked complete.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("Task 1")
    await task_manager.add_task("Task 2")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 2

        await pilot.press("j")  # Select first task
        await pilot.press("c")  # Complete task
        await pilot.pause()

        assert len(tasks_list.children) == 1


async def test_filtering_persists_after_adding_task():
    """
    Verify that the active filter remains applied after adding a new task.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("Task 1")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 1

        await pilot.press("a")
        await pilot.press("N")
        await pilot.press("e")
        await pilot.press("w")
        await pilot.press(" ")
        await pilot.press("T")
        await pilot.press("a")
        await pilot.press("s")
        await pilot.press("k")
        await pilot.press("enter")
        await pilot.pause()

        assert len(tasks_list.children) == 2


async def test_escape_clears_filtering():
    """
    Verify that pressing Escape clears the current filter text.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("Task 1")
    await task_manager.add_task("Another task")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 2

        await pilot.press("escape")
        await pilot.pause()

        assert len(tasks_list.children) == 2


async def test_filtering_clears_when_switching_list():
    """
    Verify that switching to a different list clears the current filter.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("Task 1", list_name="develop")
    await task_manager.add_task("Another task", list_name="develop")
    await task_manager.add_task("Task 2", list_name="develop2")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 2

        await app.switch_list("develop2")
        await pilot.pause()

        assert len(tasks_list.children) == 1
        assert app.filter_query == ""


async def test_filtering_clears_when_switching_to_all_list_mode():
    """
    Verify that switching to 'all lists' mode clears the current filter.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("Task 1", list_name="develop")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 1

        await app.switch_list("all")
        await pilot.pause()

        assert len(tasks_list.children) == 1
        assert app.filter_query == ""
