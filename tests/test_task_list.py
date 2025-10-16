import pytest
from lazytask.presentation.app import LazyTaskApp, TaskListItem
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from typing import cast

# INFO:
# Passed test fixes through:
# 1. Root cause: ListView.clear() is an async method that wasn't being awaited, causing old tasks to remain in the
# ListView when new tasks were appended
# 2. Fix: Added await to all three ListView.clear() calls in lazytask/presentation/app.py:243, 168, and consolidated the
# third instance at line 339 to use the existing switch_list method which now properly awaits clear()


@pytest.mark.asyncio
async def test_toggle_completed_tasks(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that toggling the completed tasks view works correctly."""
    await mock_task_manager.clear_tasks()
    await mock_task_manager.add_task("incomplete task")
    completed_task = await mock_task_manager.add_task("completed task")
    await mock_task_manager.complete_task(completed_task.id)

    async with app.run_test() as pilot:
        await app.update_tasks_list()
        await pilot.pause()
        tasks_list = app.query_one("ListView")

        # Initially, assert that only incomplete tasks are shown.
        assert len(tasks_list.children) == 1

        # Simulate the user pressing 'ctrl+c'.
        await pilot.press("ctrl+c")
        await pilot.pause()

        # Assert that both completed and incomplete tasks are shown.
        assert len(tasks_list.children) == 2

        # Simulate the user pressing 'ctrl+c' again.
        await pilot.press("ctrl+c")
        await pilot.pause()

        # Assert that only incomplete tasks are shown again.
        assert len(tasks_list.children) == 1


@pytest.mark.asyncio
async def test_completing_task_selects_next_one(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that completing a task selects the next task in the list."""
    await mock_task_manager.clear_tasks()
    await mock_task_manager.add_task("task 1")
    await mock_task_manager.add_task("task 2")
    await mock_task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        await pilot.press("ctrl+r")  # Refresh to load tasks
        await pilot.pause()

        tasks_list = app.query_one("ListView")

        # Assert that there are 3 tasks
        assert len(app.query("TaskListItem")) == 3

        # Select the second task
        await pilot.press("j")
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 1

        # Complete the second task
        await pilot.press("c")
        await pilot.pause()

        # Assert that there are 2 tasks left
        assert len(app.query("TaskListItem")) == 2

        # Assert that the new second task is selected (which was the third one)
        assert tasks_list.index == 1
        highlighted_task = cast(TaskListItem, tasks_list.highlighted_child)
        assert highlighted_task is not None
        assert highlighted_task.data.title == "task 3"

        # Complete the now-second task
        await pilot.press("c")
        await pilot.pause()

        # Assert that there is 1 task left
        assert len(app.query("TaskListItem")) == 1

        # Assert that the first task is now selected
        tasks_list = app.query_one("ListView")  # Re-query
        assert tasks_list.index == 0
        highlighted_task = cast(TaskListItem, tasks_list.highlighted_child)
        assert highlighted_task is not None
        assert highlighted_task.data.title == "task 1"


@pytest.mark.asyncio
async def test_all_tasks_render_in_list_view(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    await mock_task_manager.clear_tasks()
    titles = [f"bulk task {index}" for index in range(10)]
    for title in titles:
        await mock_task_manager.add_task(title)

    async with app.run_test() as pilot:
        await app.update_tasks_list()
        await pilot.pause()

        tasks_list = app.query_one("ListView")
        assert len(tasks_list.children) == len(titles)


@pytest.mark.asyncio
async def test_tasks_list_has_no_vertical_gap(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    await mock_task_manager.clear_tasks()
    await mock_task_manager.add_task("gap task 1")
    await mock_task_manager.add_task("gap task 2")
    async with app.run_test() as pilot:
        await app.update_tasks_list()
        await pilot.pause()
        tasks_list = app.query_one("ListView#tasks_list")
        row_gap_value = tasks_list.styles.row_gap.value
        assert row_gap_value == 0
        for task_item in app.query("TaskListItem"):
            assert task_item.styles.margin.top.value == 0
            assert task_item.styles.margin.bottom.value == 0
