import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.presentation.app import LazyTaskApp
from lazytask.domain.task import Task


@pytest.fixture
def app() -> LazyTaskApp:
    # Mock the use case dependencies
    app = LazyTaskApp()
    app.add_task_uc = AsyncMock()
    app.get_tasks_uc = MagicMock()
    app.get_tasks_uc.execute = AsyncMock(return_value=[Task(id="1", title="Test Task")])
    app.complete_task_uc = AsyncMock()
    app.update_task_uc = AsyncMock()
    app.get_lists_uc = MagicMock()
    app.get_lists_uc.execute = AsyncMock(return_value=["develop", "develop2"])
    return app


async def test_context_sensitive_actions(app: LazyTaskApp):
    async with app.run_test() as pilot:
        # Spy on the action methods
        app.action_complete_task = AsyncMock()
        app.action_edit_date = AsyncMock()
        app.action_move_to_tomorrow = AsyncMock()
        app.action_edit_task = AsyncMock()

        await pilot.pause()
        # Press keys for context-sensitive actions
        await pilot.press("c")  # complete_task
        await pilot.press("e")  # edit_date
        await pilot.press("t")  # move_to_tomorrow
        await pilot.press("meta+e")  # edit_task

        # Check that the actions were not called
        app.action_complete_task.assert_not_called()
        app.action_edit_date.assert_not_called()
        app.action_move_to_tomorrow.assert_not_called()
        app.action_edit_task.assert_not_called()

        # Add a task to the list
        await app.update_tasks_list()
        await pilot.pause()

        # Select the task
        tasks_list = app.query_one("#tasks_list")
        tasks_list.index = 0
        await pilot.pause()

        # Press keys for context-sensitive actions
        await pilot.press("c")  # complete_task
        await pilot.press("e")  # edit_date
        await pilot.press("t")  # move_to_tomorrow
        await pilot.press("meta+e")  # edit_task

        # Check that the actions were called
        app.action_complete_task.assert_called_once()
        app.action_edit_date.assert_called_once()
        app.action_move_to_tomorrow.assert_called_once()
        app.action_edit_task.assert_called_once()