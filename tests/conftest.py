import pytest
from lazytask.container import container
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture(autouse=True)
def in_memory_task_manager():
    container.set_task_manager(MockTaskManager(use_persistence=False))
