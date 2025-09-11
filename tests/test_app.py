
from lazytask.presentation.app import LazyTaskApp
from textual.pilot import Pilot

async def test_quit_app():
    """Test that the app quits when 'q' is pressed."""
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.press("q")
        assert app.is_running is False
