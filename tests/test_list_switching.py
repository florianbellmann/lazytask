import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from textual.widgets import ListView


@pytest.mark.asyncio
async def test_switch_list_with_number_keys(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2,inbox,work")
    """Test that switching lists with number keys works."""
    app = LazyTaskApp()

    # Create mock use cases
    mock_get_lists_uc = MagicMock()
    mock_get_lists_uc.execute = AsyncMock(return_value=["inbox", "work"])

    mock_get_tasks_uc = MagicMock()
    inbox_task = Task(id="1", title="Task in inbox")
    work_task = Task(id="2", title="Task in work")
    develop_task = Task(id="3", title="Task in develop")
    develop2_task = Task(id="4", title="Task in develop2")

    async def get_tasks_side_effect(list_name, include_completed=False):
        if list_name == "inbox":
            return [inbox_task]
        if list_name == "work":
            return [work_task]
        if list_name == "develop":
            return [develop_task]
        if list_name == "develop2":
            return [develop2_task]
        return []

    mock_get_tasks_uc.execute = AsyncMock(side_effect=get_tasks_side_effect)

    app.get_lists_uc = mock_get_lists_uc
    app.get_tasks_uc = mock_get_tasks_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        # Initially, it should be the default list
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop"

        # Press '2' to switch to the first list 'develop'
        await pilot.press("2")
        await pilot.pause()
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop"

        # Press '3' to switch to the second list 'develop2'
        await pilot.press("3")
        await pilot.pause()
        assert app.current_list == "develop2"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop2"

        # Press '4' to switch to the third list 'inbox'
        await pilot.press("4")
        await pilot.pause()
        assert app.current_list == "inbox"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in inbox"

        # Press '5' to switch to the fourth list 'work'
        await pilot.press("5")
        await pilot.pause()
        assert app.current_list == "work"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in work"
