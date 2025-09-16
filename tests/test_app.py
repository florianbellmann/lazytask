import pytest
from unittest.mock import AsyncMock

from lazytask.presentation.app import LazyTaskApp


async def test_quit_app():
    """Test that the app quits when 'q' is pressed."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert app._exit is True