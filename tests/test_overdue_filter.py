import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from textual.widgets import ListView


@pytest.mark.asyncio
async def test_toggle_overdue_filter(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")
    """Test that toggling the overdue filter works."""
    app = LazyTaskApp()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    tasks = [
        Task(id="1", title="Overdue task", due_date=yesterday),
        Task(id="2", title="Due today task", due_date=today),
        Task(id="3", title="Future task", due_date=tomorrow),
        Task(id="4", title="Task with no due date"),
    ]

    mock_get_tasks_uc = MagicMock()
    mock_get_tasks_uc.execute = AsyncMock(return_value=tasks)
    app.get_tasks_uc = mock_get_tasks_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        list_view = app.query_one(ListView)
        assert len(list_view.children) == 4

        # Press ctrl+d to show only overdue tasks
        await pilot.press("ctrl+d")
        await pilot.pause()

        assert app.show_overdue_only is True
        assert len(list_view.children) == 2

        # Press ctrl+d again to show all tasks
        await pilot.press("ctrl+d")
        await pilot.pause()

        assert app.show_overdue_only is False
        assert len(list_view.children) == 4
