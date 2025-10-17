import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from textual.widgets import ListView


@pytest.mark.asyncio
async def test_toggle_overdue_filter(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test that toggling the overdue filter works."""
    app = LazyTaskApp()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    tasks = [
        Task(id="1", title="Overdue task", due_date=yesterday, list_name="develop"),
        Task(id="2", title="Due today task", due_date=today, list_name="develop"),
        Task(id="3", title="Future task", due_date=tomorrow, list_name="develop"),
        Task(id="4", title="Task with no due date", list_name="develop"),
    ]

    mock_get_tasks_uc = MagicMock()

    async def get_tasks_side_effect(list_name, include_completed=False):
        if list_name == "develop":
            return tasks
        return []

    mock_get_tasks_uc.execute = AsyncMock(side_effect=get_tasks_side_effect)
    app.get_tasks_uc = mock_get_tasks_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        list_view = app.query_one(ListView)
        # App starts on "all" but only overdue tasks are shown by default
        assert app.show_overdue_only is True
        assert len(list_view.children) == 2

        # Press ctrl+d to show all tasks
        await pilot.press("ctrl+d")
        await pilot.pause()

        assert app.show_overdue_only is False
        assert len(list_view.children) == 4

        # Press ctrl+d again to show overdue tasks only
        await pilot.press("ctrl+d")
        await pilot.pause()

        assert app.show_overdue_only is True
        assert len(list_view.children) == 2
