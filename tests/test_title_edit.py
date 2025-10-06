from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.text_input_modal import TextInputModal
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from textual.widgets import Input
import pytest


@pytest.mark.asyncio
async def test_edit_title_hotkey(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user presses the hotkey to edit the title of a selected task,
    a modal should appear with the current title.
    """
    await mock_task_manager.add_task("initial title", list_name="develop")

    async with app.run_test() as pilot:
        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("r")
        await pilot.pause()

        assert len(app.screen_stack) == 2
        modal = app.screen
        assert isinstance(modal, TextInputModal)
        assert modal.query_one(Input).value == "initial title"


@pytest.mark.asyncio
async def test_edit_title_updates_task(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user edits a task's title and submits the modal,
    the title should be updated correctly.
    """
    task = await mock_task_manager.add_task("initial title", list_name="develop")

    async with app.run_test() as pilot:
        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("r")
        await pilot.pause()

        # Edit the title
        modal = app.screen
        input_widget = modal.query_one(Input)
        input_widget.value = "updated title"
        await pilot.pause()

        # Submit the modal
        await pilot.click("#submit")
        await pilot.pause()

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.title == "updated title"


@pytest.mark.asyncio
async def test_edit_title_without_selection_does_nothing(app: LazyTaskApp):
    """
    When the user presses 'r' without a task selected,
    no modal should appear.
    """
    async with app.run_test() as pilot:
        await pilot.press("r")
        await pilot.pause()

        assert len(app.screen_stack) == 1  # Only main screen
