
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


async def test_quit_app():
    """Test that the app quits when 'q' is pressed."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert app._exit is True


async def test_app_starts_without_crashes():
    """
    Verify that the application starts up cleanly without crashing.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app._running


async def test_app_quits_on_q_press():
    """
    Verify that the application exits cleanly when the user presses 'Q'.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert app._exit


async def test_reselect_previous_task_after_completion():
    """Test that the same index is selected after a task is completed."""
    app = LazyTaskApp()
    task_manager = container.task_manager
    task1 = await task_manager.add_task("task 1")
    task2 = await task_manager.add_task("task 2")
    task3 = await task_manager.add_task("task 3")

    async with app.run_test() as pilot:
        tasks_list = app.query_one("ListView")

        # Select a task in the middle of the list.
        await pilot.press("j")  # move to second task
        await pilot.pause()
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child._task.id == task2.id

        # Simulate the user pressing 'c' to complete the task.
        await pilot.press("c")
        await pilot.pause()

        # Assert that the task is completed
        tasks = await task_manager.get_tasks(include_completed=False)
        assert len(tasks) == 2

        # Assert that the next task is now selected.
        # The current behavior is to keep the same index, which means the next
        # task in the list is selected.
        assert tasks_list.index == 1
        assert tasks_list.highlighted_child._task.id == task3.id
