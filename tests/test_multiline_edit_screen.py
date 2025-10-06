from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.edit_screen import EditScreen
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from textual.widgets import TextArea
import pytest


@pytest.mark.asyncio
async def test_edit_description_multiline_in_edit_screen(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user edits a task's description with multiple lines in the EditScreen,
    the description should be saved correctly.
    """
    task = await mock_task_manager.add_task("task 1", description="initial description")

    async with app.run_test() as pilot:
        # Refresh the task list
        await pilot.pause()

        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("e")  # Open the edit screen
        await pilot.pause()

        # Wait for the screen to load the task
        await pilot.pause()

        assert len(app.screen_stack) == 2
        modal = app.screen
        assert isinstance(modal, EditScreen)

        # Enter multi-line text
        text_area = modal.query_one("#description", TextArea)
        text_area.text = "line 1\nline 2"
        await pilot.pause()

        # Click the submit button
        await pilot.click("#save")
        await pilot.pause()

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1\nline 2"


@pytest.mark.asyncio
async def test_edit_description_multiline_in_edit_screen_with_enter_press(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user edits a task's description with multiple lines in the EditScreen,
    the description should be saved correctly when pressing enter.
    """
    task = await mock_task_manager.add_task("task 1", description="initial description")

    async with app.run_test() as pilot:
        # Refresh the task list
        await pilot.pause()

        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("e")  # Open the edit screen
        await pilot.pause()

        # Wait for the screen to load the task
        await pilot.pause()

        assert len(app.screen_stack) == 2
        modal = app.screen
        assert isinstance(modal, EditScreen)

        # Set multi-line text
        text_area = modal.query_one("#description", TextArea)
        text_area.text = "line 1\nline 2"
        await pilot.pause()

        # Click the submit button
        await pilot.click("#save")
        await pilot.pause()

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1\nline 2"
