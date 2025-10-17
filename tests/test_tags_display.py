import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.domain.task import Task
import datetime


@pytest.mark.asyncio
async def test_tags_display_in_list_view(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")

    app = LazyTaskApp()
    app.show_overdue_only = False

    # Mock the task manager to control the tasks
    class MockTaskManager:
        async def get_tasks(self, list_name: str, include_completed: bool = False):
            if list_name == "develop":
                return [
                    Task(
                        id="1",
                        title="Task with tags",
                        tags=["work", "urgent"],
                        due_date=datetime.date(2025, 10, 18),
                        list_name="develop",
                    )
                ]
            return []

        async def get_lists(self) -> list[str]:
            return ["develop", "develop2"]

    app.get_tasks_uc.task_manager = MockTaskManager()

    async with app.run_test() as pilot:
        await pilot.pause()

        # The list should be updated on mount
        list_view = app.query_one("#tasks_list")

        # Switch to the "develop" list to see the task
        await app.switch_list("develop")
        await pilot.pause()

        # Check the content of the first item in the list view
        item = list_view.children[0]

        # The rendered output is complex, so we check the task data
        assert item.data.tags == ["work", "urgent"]

        # To be more thorough, we can inspect the rendered text if we know the format
        # This depends on the implementation of TaskListItem.compose()
        # For example, if it renders as "(tags: work,urgent)", we could check for that.
        # Based on the current implementation, it should be in the meta_parts

        # Let's check the composed elements to be sure
        assert "tags: work,urgent" in item.meta_parts
