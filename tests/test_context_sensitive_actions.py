import pytest
from unittest.mock import Mock

from lazytask.presentation.app import LazyTaskApp


@pytest.fixture
def app() -> LazyTaskApp:
    return LazyTaskApp()


async def test_context_sensitive_actions(app: LazyTaskApp):
    async with app.run_test() as pilot:
        # Check that the context-sensitive actions are disabled when the app starts
        for key in app.context_sensitive_actions:
            assert not app.bindings.get_key(key).enabled

        # Add a task to the list
        await app.add_task("Test Task")
        await pilot.pause()

        # Select the task
        tasks_list = app.query_one("#tasks_list")
        tasks_list.index = 0
        await pilot.pause()

        # Check that the context-sensitive actions are enabled
        for key in app.context_sensitive_actions:
            assert app.bindings.get_key(key).enabled

        # Clear the selection
        tasks_list.index = None
        await pilot.pause()

        # Check that the context-sensitive actions are disabled
        for key in app.context_sensitive_actions:
            assert not app.bindings.get_key(key).enabled