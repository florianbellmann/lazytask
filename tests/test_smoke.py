import pytest
from textual.keys import Keys
from textual.widgets import Label

from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.sort_options_screen import (
    SORT_OPTIONS,
    SortOptionsScreen,
)


@pytest.mark.asyncio
async def test_smoke_test_workflow(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    async with app.run_test() as pilot:
        await pilot.pause()
        # 1. Fire up the app (already done by app.run_test())

        # 2. Add 2 tasks to the first list ("develop")
        await pilot.press("a")
        await pilot.press(*"Task 1 Develop")
        await pilot.press(Keys.Enter)
        await pilot.pause()
        await pilot.press("a")
        await pilot.press(*"Task 2 Develop")
        await pilot.press(Keys.Enter)
        await pilot.pause()

        # Assert tasks are in the list
        tasks_list_view = app.query_one("#tasks_list")
        assert len(tasks_list_view.children) == 2
        assert "Task 1 Develop" in str(
            tasks_list_view.children[0]
            .query_one("Label#task-title", Label)
            .render()
        )
        assert "Task 2 Develop" in str(
            tasks_list_view.children[1]
            .query_one("Label#task-title", Label)
            .render()
        )

        # 3. Add 2 tasks to the second list ("develop2")
        await app.switch_list("develop2")
        await pilot.pause()
        await pilot.press("a")
        await pilot.press(*"Task 1 Develop2")
        await pilot.press(Keys.Enter)
        await pilot.pause()
        await pilot.press("a")
        await pilot.press(*"Task 2 Develop2")
        await pilot.press(Keys.Enter)
        await pilot.pause()

        assert "Task 1 Develop2" in str(
            tasks_list_view.children[0]
            .query_one("Label#task-title", Label)
            .render()
        )
        assert "Task 2 Develop2" in str(
            tasks_list_view.children[1]
            .query_one("Label#task-title", Label)
            .render()
        )

        # Switch back to develop list
        await app.switch_list("develop")
        await pilot.pause()

        # 4. List them (already asserted above)

        # 5. Change sorting using the modal
        async def choose_sort_option(option_label: str) -> None:
            await pilot.press("ctrl+o")
            await pilot.pause()
            assert isinstance(app.screen, SortOptionsScreen)
            sort_screen = app.screen
            sort_list_view = sort_screen.query_one("ListView")
            for index, option in enumerate(SORT_OPTIONS):
                if option.label == option_label:
                    sort_list_view.index = index
                    break
            await pilot.pause()
            await pilot.press(Keys.Enter)
            await pilot.pause()

        await choose_sort_option("Title ↑")
        await choose_sort_option("Creation date ↑")
        await choose_sort_option("Due date ↑")

        # 6. Filter
        await pilot.press("/")
        await pilot.press(*"Task 1")
        await pilot.press(Keys.Enter)
        await pilot.pause()
        tasks_list_view = app.query_one("#tasks_list")
        assert len(tasks_list_view.children) == 1
        assert "Task 1 Develop" in str(
            tasks_list_view.children[0]
            .query_one("Label#task-title", Label)
            .render()
        )

        # 7. Complete one item
        await pilot.press("c")  # Complete the highlighted task (Task 1 Develop)
        await pilot.pause()
        # Since completed tasks are hidden by default, the list should now be empty
        tasks_list_view = app.query_one("#tasks_list")
        assert len(tasks_list_view.children) == 0

        # 8. Remove filter
        await pilot.press("escape")
        await pilot.pause()
        # Now all tasks in 'develop' should be visible, including the completed one if show_completed is true
        # By default, show_completed is false, so only '[ ] Task 2 Develop' should be visible
        tasks_list_view = app.query_one("#tasks_list")
        assert len(tasks_list_view.children) == 1
        assert "Task 2 Develop" in str(
            tasks_list_view.children[0]
            .query_one("Label#task-title", Label)
            .render()
        )

        # 9. Change the list view (to develop2)
        await app.switch_list("develop2")
        await pilot.pause()
        tasks_list_view = app.query_one("#tasks_list")
        assert len(tasks_list_view.children) == 2
        assert "Task 1 Develop2" in str(
            tasks_list_view.children[0]
            .query_one("Label#task-title", Label)
            .render()
        )
        assert "Task 2 Develop2" in str(
            tasks_list_view.children[1]
            .query_one("Label#task-title", Label)
            .render()
        )

        # 10. Remove the other items that the smoke test created
        # The prompt asks to remove items, but there's no explicit delete action in the app's keybindings.
        # For now, we'll rely on the MockTaskManager being reset for each test.
        # If a delete action is added, this step would involve navigating to each task and pressing 'd' or similar.

        # 11. Close the app
        await pilot.press("q")
