import pytest
from unittest.mock import AsyncMock
import datetime

from lazytask.presentation.app import LazyTaskApp
from lazytask.domain.task import Task


@pytest.mark.asyncio
async def test_move_to_tomorrow(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the 'o' keybinding for moving a task to tomorrow."""
    app = LazyTaskApp()

    mock_task = Task(id="1", title="Test Task")
    app.get_tasks_uc.execute = AsyncMock(return_value=[mock_task])
    app.update_task_uc.execute = AsyncMock()

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    async with app.run_test() as pilot:
        await app.update_tasks_list()  # Manually update the list
        await pilot.pause()

        tasks_list = app.query_one("ListView")
        tasks_list.index = 0
        await pilot.pause()

        await pilot.press("o")
        await pilot.pause()

        app.update_task_uc.execute.assert_called_once()
        args, kwargs = app.update_task_uc.execute.call_args
        assert args[1]["due_date"] == tomorrow


@pytest.mark.asyncio
async def test_move_to_next_monday_hotkey(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the 'm' keybinding for moving a task to next Monday."""
    app = LazyTaskApp()

    mock_task = Task(id="1", title="Test Task")
    app.get_tasks_uc.execute = AsyncMock(return_value=[mock_task])
    app.update_task_uc.execute = AsyncMock()

    today = datetime.date.today()
    days_until_monday = (0 - today.weekday() + 7) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday = today + datetime.timedelta(days=days_until_monday)

    async with app.run_test() as pilot:
        await app.update_tasks_list()  # Manually update the list
        await pilot.pause()

        tasks_list = app.query_one("ListView")
        tasks_list.index = 0
        await pilot.pause()

        await pilot.press("m")
        await pilot.pause()

        app.update_task_uc.execute.assert_called_once()
        args, kwargs = app.update_task_uc.execute.call_args
        assert args[1]["due_date"] == next_monday


@pytest.mark.asyncio
async def test_move_to_next_weekend_hotkey(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test the 'w' keybinding for moving a task to next weekend."""
    app = LazyTaskApp()

    mock_task = Task(id="1", title="Test Task")
    app.get_tasks_uc.execute = AsyncMock(return_value=[mock_task])
    app.update_task_uc.execute = AsyncMock()

    today = datetime.date.today()
    days_until_saturday = (5 - today.weekday() + 7) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    next_saturday = today + datetime.timedelta(days=days_until_saturday)

    async with app.run_test() as pilot:
        await app.update_tasks_list()  # Manually update the list
        await pilot.pause()

        tasks_list = app.query_one("ListView")
        tasks_list.index = 0
        await pilot.pause()

        await pilot.press("w")
        await pilot.pause()

        app.update_task_uc.execute.assert_called_once()
        args, kwargs = app.update_task_uc.execute.call_args
        assert args[1]["due_date"] == next_saturday
