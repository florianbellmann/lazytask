import pytest
from lazytask.presentation.app import LazyTaskApp, TaskListItem
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from typing import cast


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
        await app.update_tasks_list()
        tasks_list = app.query_one("ListView")
        await pilot.pause()

        # Assert that there are 3 tasks
        assert len(tasks_list.children) == 3

        # Select the second task
        await pilot.press("j")
        await pilot.pause()
        assert tasks_list.index == 1

        # Complete the second task
        await pilot.press("c")
        await pilot.pause()

        # Assert that there are 2 tasks left
        assert len(tasks_list.children) == 2

        # Assert that the new second task is selected (which was the third one)
        assert tasks_list.index == 1
        highlighted_task = cast(TaskListItem, tasks_list.highlighted_child)
        assert highlighted_task is not None
        assert highlighted_task.data.title == "task 3"

        # Complete the now-second task
        await pilot.press("c")
        await pilot.pause()

        # Assert that there is 1 task left
        assert len(tasks_list.children) == 1

        # Assert that the first task is now selected
        assert tasks_list.index == 0
        highlighted_task = cast(TaskListItem, tasks_list.highlighted_child)
        assert highlighted_task is not None
        assert highlighted_task.data.title == "task 1"
