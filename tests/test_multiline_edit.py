import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from tests.stubs import StubDescriptionEditor


@pytest.mark.asyncio
async def test_edit_description_cancel_keeps_original_text(
    app: LazyTaskApp,
    mock_task_manager: MockTaskManager,
    description_editor_stub: StubDescriptionEditor,
):
    """
    If the external editor returns None (cancel), the task description remains unchanged.
    """
    task = await mock_task_manager.add_task("task 1", description="line 1")
    description_editor_stub.next_response = None

    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        await pilot.pause(0.05)

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1"
