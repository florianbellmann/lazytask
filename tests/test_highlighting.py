import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")



async def test_navigation_j_k_changes_highlight_and_selection():
    """
    Using 'J' moves the highlight/selection down one item; using 'K' moves it up one item.
    Both highlight and selection change together and remain in sync.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1")
    await task_manager.add_task("task 2")
    await task_manager.add_task("task 3")

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


async def test_highlight_always_matches_selection():
    """
    The highlighted task is always the selected task; they never diverge.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1")
    await task_manager.add_task("task 2")

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


async def test_selection_and_highlight_reset_to_first_on_list_switch():
    """
    When switching to another list, set highlight/selection to the first item.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1", list_name="develop")
    await task_manager.add_task("task 2", list_name="develop")
    await task_manager.add_task("task 3", list_name="develop2")

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


async def test_selection_after_completing_task():
    """
    When completing the currently selected task:
      - Select/highlight the task below it, if any.
      - Otherwise select/highlight the previous task (above), if any.
      - If neither exists (list becomes empty), select/highlight nothing.
    """
    # Case 1: complete task in the middle
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.clear_tasks()
    await task_manager.add_task("task 1")
    await task_manager.add_task("task 2")
    await task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")
        await pilot.press("j")  # select task 1
        await pilot.press("j")  # select task 2
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 2"

        await pilot.press("c")  # complete task 2
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 3"

    # Case 2: complete last task
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.clear_tasks()
    await task_manager.add_task("task 1")
    await task_manager.add_task("task 2")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")
        await pilot.press("j")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 2"

        await pilot.press("c")  # complete task 2
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 1"

    # Case 3: complete only task
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.clear_tasks()
    await task_manager.add_task("task 1")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.highlighted_child.data.title == "task 1"

        await pilot.press("c")  # complete task 1
        await pilot.pause()
        assert tasks_list.highlighted_child is None


async def test_selection_and_highlight_move_to_new_task_after_adding():
    """
    After adding a new task, highlight/select the newly added task.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1")

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

        assert len(tasks_list.children) == 2
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child.data.title == "test"


async def test_filtering_keeps_current_selection_unless_filtered_out_then_first_else_none():
    """
    While filtering:
      - Keep the current highlight/selection if the selected task still matches the filter.
      - If it no longer matches, select/highlight the first item in the filtered list.
      - If the filtered list is empty, select/highlight nothing.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("apple")
    await task_manager.add_task("banana")
    await task_manager.add_task("apricot")

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
