import pytest
import logging
import os
from lazytask.application.use_cases import AddTask
from lazytask.infrastructure.mock_task_manager import MockTaskManager

# Note: This test requires a logging statement in the AddTask use case.
# The logging statement was removed from the application code, so this test will fail.

LOG_FILE = "lazytask.log"


@pytest.fixture
def task_manager():
    return MockTaskManager()


def configure_logging():
    # Remove all existing handlers
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


@pytest.fixture(autouse=True)
def setup_logging():
    # Remove the log file if it exists
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    yield
    # Clean up: remove all handlers
    for handler in logging.getLogger().handlers[:]:
        handler.close()
        logging.getLogger().removeHandler(handler)
    # Remove the log file after the test
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)


@pytest.mark.asyncio
async def test_add_task_logs_message(task_manager):
    configure_logging()
    add_task_uc = AddTask(task_manager)
    title = "Log Test Task"
    await add_task_uc.execute(title)

    with open(LOG_FILE, "r") as f:
        log_output = f.read()

    assert f"INFO:root:Adding task with title: {title}" in log_output
