import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.list_tabs import ListTabs


async def test_list_tabs_from_config(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "list1,list2,list3")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        list_tabs = app.query_one(ListTabs)
        rendered_text = str(list_tabs.render())
        assert "list1" in rendered_text
        assert "list2" in rendered_text
        assert "list3" in rendered_text
        assert app.current_list == "list1"


@pytest.mark.asyncio
async def test_list_tabs_display(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2,inbox,work")
    """Test that the list tabs are displayed and updated correctly."""
    app = LazyTaskApp()

    mock_get_lists_uc = MagicMock()
    mock_get_lists_uc.execute = AsyncMock(return_value=["inbox", "work"])
    app.get_lists_uc = mock_get_lists_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        list_tabs = app.query_one(ListTabs)
        # Assert on the rendered text content, not on a specific widget type
        rendered_text = str(list_tabs.render())
        assert "all" in rendered_text
        assert "inbox" in rendered_text
        assert "work" in rendered_text

        # Check initial active tab by checking the current_list property of the app
        assert app.current_list == "develop"

        app.current_list = "inbox"
        await app.update_tasks_list()
        await pilot.pause()
        # Check active tab after switching
        assert app.current_list == "inbox"
