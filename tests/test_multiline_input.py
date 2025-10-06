
import pytest
from textual.widgets import TextArea
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.text_input_modal import TextInputModal


@pytest.mark.asyncio
async def test_add_multiline_description(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user adds a multi-line description to a new task,
    the description should be saved correctly.
    """
    task = await mock_task_manager.add_task("task 1")
    assert task.description is None

    async with app.run_test() as pilot:
        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("e")  # edit description
        await pilot.pause()

        # Check that the modal is open
        assert isinstance(app.screen, TextInputModal)

        # Type in the description
        await pilot.press("line 1")
        await pilot.press("enter")
        await pilot.press("line 2")

        # Submit the modal
        await pilot.click("#submit")
        await pilot.pause()

        # Check that the description was updated
        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1\nline 2"

