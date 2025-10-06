from unittest.mock import AsyncMock

from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager


async def test_context_sensitive_actions(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    async with app.run_test() as pilot:
        # Spy on the action methods
        app.action_complete_task = AsyncMock()
        app.action_edit_date = AsyncMock()
        app.action_move_to_tomorrow = AsyncMock()
        app.action_due_today = AsyncMock()
        app.action_edit_description = AsyncMock()

        await pilot.pause()
        # Press keys for context-sensitive actions (no task selected)
        await pilot.press("c")  # complete_task
        await pilot.press("d")  # edit_date
        await pilot.press("o")  # move_to_tomorrow
        await pilot.press("t")  # due_today
        await pilot.press("e")  # edit_description

        # Check that the actions were NOT called
        app.action_complete_task.assert_not_called()
        app.action_edit_date.assert_not_called()
        app.action_move_to_tomorrow.assert_not_called()
        app.action_due_today.assert_not_called()
        app.action_edit_description.assert_not_called()

        # Add a task to the list
        await mock_task_manager.add_task(title="Test Task", list_name="develop")
        await app.update_tasks_list()
        await pilot.pause()

        # Select the task
        tasks_list = app.query_one("#tasks_list")
        tasks_list.index = 0
        await pilot.pause()  # Ensure UI updates

        # Press keys for context-sensitive actions (task selected)
        await pilot.press("c")  # complete_task
        await pilot.press("d")  # edit_date
        await pilot.press("o")  # move_to_tomorrow
        await pilot.press("t")  # due_today
        await pilot.press("e")  # edit_description

        # Check that the actions WERE called
        app.action_complete_task.assert_called_once()
        app.action_edit_date.assert_called_once()
        app.action_move_to_tomorrow.assert_called_once()
        app.action_due_today.assert_called_once()
        app.action_edit_description.assert_called_once()
