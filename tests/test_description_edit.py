from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.text_input_modal import TextInputModal
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.widgets.text_area import TextArea
import pytest


@pytest.mark.asyncio
async def test_edit_description_hotkey(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user presses the hotkey to edit the description of a selected task,
    a modal should appear with the current description.
    """
    await mock_task_manager.add_task("task 1", description="initial description")

    async with app.run_test() as pilot:
        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        assert len(app.screen_stack) == 2
        modal = app.screen
        assert isinstance(modal, TextInputModal)
        assert modal.query_one(TextArea).text == "initial description"


@pytest.mark.asyncio
async def test_edit_description_multiline(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user edits a task's description with multiple lines,
    the description should be saved correctly.
    """
    task = await mock_task_manager.add_task("task 1", description="initial description")

    async with app.run_test() as pilot:
        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        # Enter multi-line text
        modal = app.screen
        text_area = modal.query_one(TextArea)
        text_area.text = "line 1\nline 2"
        await pilot.pause()

        # Click the submit button
        await pilot.click("#submit")
        await pilot.pause()

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1\nline 2"