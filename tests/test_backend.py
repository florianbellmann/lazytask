import pytest
import asyncio
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.domain.task_manager import Task

@pytest.fixture
def mock_task_manager():
    return MockTaskManager()

@pytest.mark.asyncio
async def test_add_task(mock_task_manager: MockTaskManager):
    task = await mock_task_manager.add_task("Buy groceries")
    assert isinstance(task, Task)
    assert task.title == "Buy groceries"
    assert not task.completed

    tasks = await mock_task_manager.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy groceries"

@pytest.mark.asyncio
async def test_complete_task(mock_task_manager: MockTaskManager):
    task = await mock_task_manager.add_task("Do laundry")
    completed_task = await mock_task_manager.complete_task(task.id)
    assert completed_task is not None
    assert completed_task.completed

    tasks = await mock_task_manager.get_tasks()
    assert len(tasks) == 0 # Should not include completed tasks by default

    all_tasks = await mock_task_manager.get_tasks(include_completed=True)
    assert len(all_tasks) == 1
    assert all_tasks[0].completed

@pytest.mark.asyncio
async def test_get_lists(mock_task_manager: MockTaskManager):
    lists = await mock_task_manager.get_lists()
    assert "develop" in lists

    await mock_task_manager.add_task("Task in another list", list_name="personal")
    lists = await mock_task_manager.get_lists()
    assert "develop" in lists
    assert "personal" in lists
    assert len(lists) == 2