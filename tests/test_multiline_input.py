import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from tests.stubs import StubDescriptionEditor


@pytest.mark.asyncio
async def test_add_multiline_description(
    app: LazyTaskApp,
    mock_task_manager: MockTaskManager,
    description_editor_stub: StubDescriptionEditor,
):
    """
    When the external editor returns multiline text for a new task, it is stored.
    """
    task = await mock_task_manager.add_task("task 1")
    assert task.description is None
    description_editor_stub.next_response = "line 1\nline 2"

    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause(0.1)

    updated_task = await mock_task_manager.get_task(task.id, task.list_name)
    assert updated_task.description == "line 1\nline 2"
