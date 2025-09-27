from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.text_input_modal import TextInputModal
from lazytask.infrastructure.mock_task_manager import MockTaskManager
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
        assert modal.query_one("Input").value == "initial description"
