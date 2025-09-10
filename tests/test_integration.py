
import pytest
import os
from lazytask.infrastructure.reminders_cli_task_manager import RemindersCliTaskManager, REMINDERS_CLI_PATH

@pytest.fixture
def task_manager():
    return RemindersCliTaskManager()

@pytest.mark.integration
@pytest.mark.skip(reason="reminders-cli binary not available in test environment")
def test_reminders_cli_exists():
    assert os.path.exists(REMINDERS_CLI_PATH), "reminders-cli binary not found"
    assert os.access(REMINDERS_CLI_PATH, os.X_OK), "reminders-cli binary is not executable"

@pytest.mark.integration
@pytest.mark.skip(reason="reminders-cli binary not available in test environment")
@pytest.mark.asyncio
async def test_add_and_get_task(task_manager):
    # Ensure the develop list exists
    lists = await task_manager.get_lists()
    if "develop" not in lists:
        # The reminders-cli does not have a create-list command, so we can't create it.
        # For now, we'll rely on the user to have created it.
        pytest.skip("Skipping integration test: 'develop' list not found in Reminders.")

    title = "Integration Test Task"
    task = await task_manager.add_task(title, list_name="develop")
    assert task.title == title

    tasks = await task_manager.get_tasks(list_name="develop")
    assert any(t.id == task.id for t in tasks)

    # Cleanup: complete the task
    await task_manager.complete_task(task.id, list_name="develop")
