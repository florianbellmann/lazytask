import pytest
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture
def task_manager() -> MockTaskManager:
    return MockTaskManager()


@pytest.mark.asyncio
async def test_add_and_get_task(task_manager: MockTaskManager):
    """Test adding and retrieving a task using the mock task manager."""
    list_name = "develop"
    title = "Integration Test Task"

    # Add a task
    task = await task_manager.add_task(title, list_name=list_name)
    assert task.title == title

    # Retrieve tasks
    tasks = await task_manager.get_tasks(list_name=list_name)
    assert any(t.id == task.id for t in tasks)

    # Cleanup: complete the task
    await task_manager.complete_task(task.id, list_name=list_name)
    tasks = await task_manager.get_tasks(list_name=list_name, include_completed=True)
    completed_task = next((t for t in tasks if t.id == task.id), None)
    assert completed_task is not None
    assert completed_task.completed
