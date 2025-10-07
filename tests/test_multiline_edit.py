import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from textual.widgets import TextArea


@pytest.mark.asyncio
async def test_edit_description_insert_newline(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When the user presses enter in the description edit modal,
    a newline should be inserted and the text should be updated correctly.
    """
    task = await mock_task_manager.add_task("task 1", description="line 1")

    async with app.run_test() as pilot:
        await pilot.press("j")  # select task
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        # Type multiline text
        text_area = app.screen.query_one(TextArea)
        text_area.text = "line 1\nline 2"
        await pilot.pause()

        # Click the submit button
        await pilot.click("#submit")
        await pilot.pause()

        updated_task = await mock_task_manager.get_task(task.id, task.list_name)
        assert updated_task.description == "line 1\nline 2"
