import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


@pytest.mark.asyncio
async def test_toggle_completed_tasks(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test that toggling the completed tasks view works correctly."""
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("incomplete task")
    completed_task = await task_manager.add_task("completed task")
    await task_manager.complete_task(completed_task.id)

    async with app.run_test() as pilot:
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
