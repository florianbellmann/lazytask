import pytest
from lazytask.container import container
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.app import LazyTaskApp


@pytest.fixture
def mock_task_manager() -> MockTaskManager:
    task_manager = MockTaskManager(use_persistence=False)
    container.set_task_manager(task_manager)
    return task_manager


@pytest.fixture
async def app(mock_task_manager: MockTaskManager) -> LazyTaskApp:
    await mock_task_manager.clear_tasks()
    return LazyTaskApp()

