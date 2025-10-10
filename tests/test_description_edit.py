import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from tests.stubs import StubDescriptionEditor


@pytest.mark.asyncio
async def test_edit_description_hotkey(
    app: LazyTaskApp,
    mock_task_manager: MockTaskManager,
    description_editor_stub: StubDescriptionEditor,
):
    """
    Pressing the edit description hotkey should invoke the external editor with
    the current description.
    """
    await mock_task_manager.add_task("task 1", description="initial description")
    description_editor_stub.next_response = "initial description"

    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        assert description_editor_stub.calls
        _, captured_text = description_editor_stub.calls[-1]
        assert captured_text == "initial description"
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_edit_description_multiline(
    app: LazyTaskApp,
    mock_task_manager: MockTaskManager,
    description_editor_stub: StubDescriptionEditor,
):
    """
    When the user saves multi-line content from the external editor, the task is updated.
    """
    task = await mock_task_manager.add_task("task 1", description="initial description")
    description_editor_stub.next_response = "line 1\nline 2"

    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        await pilot.pause(0.1)

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1\nline 2"
