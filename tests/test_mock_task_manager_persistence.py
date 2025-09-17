import pytest
import os
import json
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture
def temp_file(tmp_path):
    return tmp_path / "test_tasks.json"


@pytest.mark.asyncio
async def test_task_persistence(temp_file):
    """Test that tasks are persisted to a file."""
    # Create a task manager and add a task
    task_manager1 = MockTaskManager(file_path=str(temp_file))
    await task_manager1.add_task("Test task")

    # Create a new task manager with the same file
    task_manager2 = MockTaskManager(file_path=str(temp_file))
    tasks = await task_manager2.get_tasks()

    # Check that the task is there
    assert len(tasks) == 1
    assert tasks[0].title == "Test task"

    # Clean up the file
    os.remove(temp_file)
