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


async def test_app_starts_in_all_view():
    """
    Verify that the application starts in the "all" view.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.current_list == "all"


def test_available_lists_trim_spaces(monkeypatch):
    """Environment list names with spaces should be trimmed."""
    monkeypatch.setenv("LAZYTASK_LISTS", " work , personal , ops ")
    app = LazyTaskApp()
    assert app.available_lists == ["work", "personal", "ops"]
