import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.list_tabs import ListTabs

@pytest.mark.asyncio
async def test_list_tabs_display():
    """Test that the list tabs are displayed and updated correctly."""
    app = LazyTaskApp()

    mock_get_lists_uc = MagicMock()
    mock_get_lists_uc.execute = AsyncMock(return_value=["inbox", "work"])
    app.get_lists_uc = mock_get_lists_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        list_tabs = app.query_one(ListTabs)
        plain_text = list_tabs.tabs.plain
        assert "all" in plain_text
        assert "inbox" in plain_text
        assert "work" in plain_text

        # Check that the current list is highlighted
        app.current_list = "inbox"
        await app.update_tasks_list()
        await pilot.pause()

        # The style is what makes it highlighted, can't easily test with plain text.
        # The mock check below is better for this.

        # Let's check the update_lists method was called with the correct arguments
        list_tabs.update_lists = MagicMock()
        app.current_list = "work"
        await app.update_tasks_list()
        await pilot.pause()
        list_tabs.update_lists.assert_called_with(["inbox", "work"], "work")
