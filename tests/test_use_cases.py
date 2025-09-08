
import pytest
from lazytask.application.use_cases import AddTask, GetAllTasks
from lazytask.infrastructure.mock_task_repository import MockTaskRepository

@pytest.mark.asyncio
async def test_add_task():
    repo = MockTaskRepository()
    add_task_uc = AddTask(repo)
    get_all_tasks_uc = GetAllTasks(repo)

    title = "Test Task"
    await add_task_uc.execute(title)

    tasks = await get_all_tasks_uc.execute()
    assert len(tasks) == 1
    assert tasks[0].title == title
