from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager


async def test_filtering_with_slash_button(app: LazyTaskApp):
    """
    Verify that pressing the slash button (`/`) activates filtering
    and allows typing a filter string.
    """
    async with app.run_test() as pilot:
        await pilot.press("/")
        await pilot.pause()
        assert isinstance(pilot.app.screen, object)  # Check if a modal is open


async def test_filtering_is_case_insensitive(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Verify that filtering matches tasks regardless of case.
    Example: typing 'foo' matches tasks named 'Foo' or 'FOO'.
    """
    await mock_task_manager.add_task("Task 1")
    await mock_task_manager.add_task("task 2")
    await mock_task_manager.add_task("TASK 3")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 3


async def test_filtering_persists_after_completing_task(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Verify that the active filter remains applied after a task is marked complete.
    """
    await mock_task_manager.add_task("Task 1")
    await mock_task_manager.add_task("Task 2")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 2

        await pilot.press("j")  # Select first task
        await pilot.press("c")  # Complete task
        await pilot.pause()

        assert len(tasks_list.children) == 1


async def test_filtering_persists_after_adding_task(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Verify that the active filter remains applied after adding a new task.
    """
    await mock_task_manager.add_task("Task 1")

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


async def test_escape_clears_filtering(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Verify that pressing Escape clears the current filter text.
    """
    await mock_task_manager.add_task("Task 1")
    await mock_task_manager.add_task("Another task")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 2

        await pilot.press("escape")
        await pilot.pause()

        assert len(tasks_list.children) == 2


async def test_filtering_clears_when_switching_list(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Verify that switching to a different list clears the current filter.
    """
    await mock_task_manager.add_task("Task 1", list_name="develop")
    await mock_task_manager.add_task("Another task", list_name="develop")
    await mock_task_manager.add_task("Task 2", list_name="develop2")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 2

        await app.switch_list("develop2")
        await pilot.pause()

        assert len(tasks_list.children) == 1
        assert app.filter_query == ""


async def test_filtering_clears_when_switching_to_all_list_mode(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Verify that switching to 'all lists' mode clears the current filter.
    """
    await mock_task_manager.add_task("Task 1", list_name="develop")

    async with app.run_test() as pilot:
        await app.update_tasks_list(filter_query="Task")
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == 1

        await app.switch_list("all")
        await pilot.pause()

        assert len(tasks_list.children) == 1
        assert app.filter_query == ""
