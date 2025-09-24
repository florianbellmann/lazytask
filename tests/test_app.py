import pytest
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    monkeypatch.setenv("LAZYTASK_DEFAULT_LIST", "develop")


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
        await pilot.pause(0.5)
        await pilot.press("q")
        await pilot.pause(0.5)
        assert app._exit
