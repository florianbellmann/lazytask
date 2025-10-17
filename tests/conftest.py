import pytest
from lazytask.container import container
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.app import LazyTaskApp
from tests.stubs import StubDescriptionEditor


@pytest.fixture
def mock_task_manager() -> MockTaskManager:
    task_manager = MockTaskManager(use_persistence=False)
    container.set_task_manager(task_manager)
    return task_manager


@pytest.fixture
def description_editor_stub() -> StubDescriptionEditor:
    editor = StubDescriptionEditor()
    container.set_description_editor(editor)
    return editor


@pytest.fixture
async def app(
    mock_task_manager: MockTaskManager,
    description_editor_stub: StubDescriptionEditor,
    monkeypatch,
) -> LazyTaskApp:
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    await mock_task_manager.clear_tasks()
    app = LazyTaskApp()
    # Most tests expect to work with the full task list; disable the overdue-only
    # filter up-front so they can operate without additional toggling.
    app.show_overdue_only = False
    return app
