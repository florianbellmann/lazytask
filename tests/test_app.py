import pytest
from lazytask.presentation.app import LazyTaskApp


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")


async def test_app_starts_without_crashes():
    """
    Verify that the application starts up cleanly without crashing.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app._running


async def test_app_quits_on_q_press():
    """
    Verify that the application exits cleanly when the user presses 'q'.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause()
        assert app._exit


async def test_app_starts_in_all_view(monkeypatch):
    """
    Verify that the application starts in the "all" view.
    """
    monkeypatch.setenv("LAZYTASK_START_VIEW", "all")
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.current_list == "all"