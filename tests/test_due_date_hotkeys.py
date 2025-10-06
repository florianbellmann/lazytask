import pytest
import datetime

from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.mark.asyncio
async def test_move_to_tomorrow(app: LazyTaskApp, mock_task_manager: MockTaskManager):
    """Test the 'o' keybinding for moving a task to tomorrow."""
    await mock_task_manager.add_task(title="Test Task", list_name="develop")
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        await pilot.press("j")  # Select the task
        await pilot.pause()

        await pilot.press("o")
        await pilot.pause(0.1)

        task_item = pilot.app.query_one("TaskListItem")
        assert task_item.data.due_date == tomorrow


@pytest.mark.asyncio
async def test_move_to_next_monday_hotkey(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test the 'm' keybinding for moving a task to next Monday."""
    await mock_task_manager.add_task(title="Test Task", list_name="develop")

    today = datetime.date.today()
    days_until_monday = (0 - today.weekday() + 7) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday = today + datetime.timedelta(days=days_until_monday)

    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        await pilot.press("j")  # Select the task
        await pilot.pause()

        await pilot.press("m")
        await pilot.pause(0.1)

        task_item = pilot.app.query_one("TaskListItem")
        assert task_item.data.due_date == next_monday


@pytest.mark.asyncio
async def test_move_to_next_weekend_hotkey(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test the 'w' keybinding for moving a task to next weekend."""
    await mock_task_manager.add_task(title="Test Task", list_name="develop")

    today = datetime.date.today()
    days_until_saturday = (5 - today.weekday() + 7) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    next_saturday = today + datetime.timedelta(days=days_until_saturday)

    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        await pilot.press("j")  # Select the task
        await pilot.pause()

        await pilot.press("w")
        await pilot.pause(0.1)

        task_item = pilot.app.query_one("TaskListItem")
        assert task_item.data.due_date == next_saturday
