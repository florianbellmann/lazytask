import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")


# INFO:
# Passed test fixes through:
# 1. Root cause: ListView.clear() is an async method that wasn't being awaited, causing old tasks to remain in the
# ListView when new tasks were appended
# 2. Fix: Added await to all three ListView.clear() calls in lazytask/presentation/app.py:243, 168, and consolidated the
# third instance at line 339 to use the existing switch_list method which now properly awaits clear()


async def test_navigation_j_k_changes_highlight_and_selection(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    Using 'J' moves the highlight/selection down one item; using 'K' moves it up one item.
    Both highlight and selection change together and remain in sync.
    """
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


async def test_highlight_always_matches_selection(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    The highlighted task is always the selected task; they never diverge.
    """
    await mock_task_manager.add_task("task 1")
    await mock_task_manager.add_task("task 2")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")
        assert tasks_list.index is None
        assert tasks_list.highlighted_child is None

        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 0
        assert tasks_list.highlighted_child is tasks_list.children[0]

        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child is tasks_list.children[1]


async def test_selection_and_highlight_reset_to_first_on_list_switch(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When switching to another list, set highlight/selection to the first item.
    """
    await mock_task_manager.add_task("task 1", list_name="develop")
    await mock_task_manager.add_task("task 2", list_name="develop")
    await mock_task_manager.add_task("task 3", list_name="develop2")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")

        # select second task in 'develop'
        await pilot.press("j")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 1

        # switch to 'develop2'
        await app.switch_list("develop2")
        await pilot.pause()

        # check that selection is reset to first item
        assert tasks_list.index == 0


async def test_selection_after_completing_task(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When completing the currently selected task:
      - Select/highlight the task below it, if any.
      - Otherwise select/highlight the previous task (above), if any.
      - If neither exists (list becomes empty), select/highlight nothing.
    """
    async with app.run_test() as pilot:
        # Case 1: complete task in the middle
        await mock_task_manager.clear_tasks()
        await mock_task_manager.add_task("task 1")
        await mock_task_manager.add_task("task 2")
        await mock_task_manager.add_task("task 3")
        await app.update_tasks_list(preserve_selection=False)

        tasks_list = app.query_one("ListView")
        await pilot.press("j")  # select task 1
        await pilot.press("j")  # select task 2
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 2"

        await pilot.press("c")  # complete task 2
        await pilot.pause(0.1)
        assert tasks_list.index == 1  # task 3 is now at index 1
        assert tasks_list.children[tasks_list.index].data.title == "task 3"

        # Case 2: complete last task
        await mock_task_manager.clear_tasks()
        await mock_task_manager.add_task("task 1")
        await mock_task_manager.add_task("task 2")
        await app.update_tasks_list(preserve_selection=False)

        tasks_list = app.query_one("ListView")
        await pilot.press("j")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 2"

        await pilot.press("c")  # complete task 2
        await pilot.pause()
        await pilot.pause()
        assert tasks_list.index == 0  # task 1 is now at index 0
        assert tasks_list.children[tasks_list.index].data.title == "task 1"

        # Case 3: complete only task
        await mock_task_manager.clear_tasks()
        await mock_task_manager.add_task("task 1")
        await app.update_tasks_list(preserve_selection=False)

        tasks_list = app.query_one("ListView")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 1"

        await pilot.press("c")  # complete task 1
        await pilot.pause()
        assert tasks_list.index is None
        assert tasks_list.highlighted_child is None


async def test_selection_and_highlight_move_to_new_task_after_adding(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    After adding a new task, highlight/select the newly added task.
    """
    await mock_task_manager.add_task("task 1")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 0

        await pilot.press("a")
        await pilot.press("t")
        await pilot.press("e")
        await pilot.press("s")
        await pilot.press("t")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()

        tasks_list.refresh()

        assert len(tasks_list.children) == 2
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child.data.title == "test"


async def test_filtering_keeps_current_selection_unless_filtered_out_then_first_else_none(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    While filtering:
      - Keep the current highlight/selection if the selected task still matches the filter.
      - If it no longer matches, select/highlight the first item in the filtered list.
      - If the filtered list is empty, select/highlight nothing.
    """
    await mock_task_manager.add_task("apple")
    await mock_task_manager.add_task("banana")
    await mock_task_manager.add_task("apricot")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")

        # Select "banana"
        await pilot.press("j")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "banana"

        # Filter for "ap"
        await pilot.press("/")
        await pilot.press("a")
        await pilot.press("p")
        await pilot.press("enter")
        await pilot.pause()

        # "banana" is filtered out, so selection should move to the first match, "apple"
        assert tasks_list.index == 0
        assert tasks_list.highlighted_child.data.title == "apple"

        # Filter for "b"
        await pilot.press("/")
        await pilot.press("b")
        await pilot.press("enter")
        await pilot.pause()

        # "banana" is now in the filtered list, but it was not selected before.
        # The selection should be on the first item, "banana".
        assert tasks_list.index == 0
        assert tasks_list.highlighted_child.data.title == "banana"

        # Filter for "z"
        await pilot.press("/")
        await pilot.press("z")
        await pilot.press("enter")
        await pilot.pause()

        # No tasks match, so nothing should be selected
        assert tasks_list.index is None
        assert tasks_list.highlighted_child is None


async def test_reselect_previous_task_after_completion(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that the same index is selected after a task is completed."""
    task1 = await mock_task_manager.add_task("task 1")
    task2 = await mock_task_manager.add_task("task 2")
    task3 = await mock_task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")

        # Select a task in the middle of the list.
        await pilot.press("j")  # move to second task
        await pilot.pause()
        await pilot.press("j")  # move to second task
        await pilot.pause()
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child.data.id == task2.id

        # Simulate the user pressing 'c' to complete the task.
        await pilot.press("c")
        await pilot.pause()
        await pilot.pause()

        # Re-query the ListView to get the new instance
        tasks_list = app.query_one("ListView")
        # Assert that the task is completed
        tasks = await mock_task_manager.get_tasks(include_completed=False)
        assert len(tasks) == 2

        # Assert that the next task is now selected.
        # The current behavior is to keep the same index, which means the next
        # task in the list is selected.
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child.data.id == task3.id
