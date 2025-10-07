import datetime
from typing import Optional

from lazytask.presentation.app import LazyTaskApp
from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.presentation.sort_options_screen import (
    SORT_OPTIONS,
    SortOptionsScreen,
)


async def select_sort_option(
    pilot,
    app: LazyTaskApp,
    option_label: str,
) -> None:
    await pilot.press("ctrl+o")
    await pilot.pause()
    assert isinstance(app.screen, SortOptionsScreen)

    sort_screen = app.screen
    sort_list_view = sort_screen.query_one("ListView")
    target_index: Optional[int] = None
    for index, option in enumerate(SORT_OPTIONS):
        if option.label == option_label:
            target_index = index
            break
    if target_index is None:
        raise AssertionError(f"Sort option '{option_label}' not found")

    sort_list_view.index = target_index
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


async def test_default_sort_due_date_oldest_first_selected_on_startup(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    On startup:
      - The selected sort is 'due date ascending' (oldest first).
      - The visible list is sorted by due date from oldest to newest.
    """
    assert app.sort_by == "due_date"
    assert app.sort_reverse is False

    await mock_task_manager.add_task("task 1", due_date=datetime.date(2025, 1, 2))
    await mock_task_manager.add_task("task 2", due_date=datetime.date(2025, 1, 1))
    await mock_task_manager.add_task("task 3", due_date=datetime.date(2025, 1, 3))

    async with app.run_test() as pilot:
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item.data.title for item in tasks_list.children]
        assert rendered_tasks == ["task 2", "task 1", "task 3"]


async def test_sort_due_date_descending_when_direction_reversed(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When switching the sort direction while on 'due date':
      - The list becomes sorted newest -> oldest.
      - Confirm it is strictly the reverse order of ascending-by-due-date.
    """
    await mock_task_manager.add_task("task 1", due_date=datetime.date(2025, 1, 2))
    await mock_task_manager.add_task("task 2", due_date=datetime.date(2025, 1, 1))
    await mock_task_manager.add_task("task 3", due_date=datetime.date(2025, 1, 3))

    async with app.run_test() as pilot:
        await pilot.press("ctrl+i")  # reverse sort
        await pilot.pause()

        assert app.sort_reverse is True
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item.data.title for item in tasks_list.children]
        assert rendered_tasks == ["task 3", "task 1", "task 2"]


async def test_sort_alphabetically_ascending(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When choosing alphabetical sort:
      - The list is sorted A -> Z by task title.
      - The selected sort reflects 'alphabetical ascending'.
    """
    await mock_task_manager.add_task("b task")
    await mock_task_manager.add_task("a task")
    await mock_task_manager.add_task("c task")

    async with app.run_test() as pilot:
        await select_sort_option(pilot, app, "Title ↑")

        assert app.sort_by == "title"
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item.data.title for item in tasks_list.children]
        assert rendered_tasks == ["a task", "b task", "c task"]


async def test_sort_alphabetically_descending(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """
    When choosing alphabetical sort reversed:
      - The list is sorted Z -> A by task title.
      - Confirm it is strictly the reverse order of alphabetical ascending.
      - The selected sort reflects 'alphabetical descending'.
    """
    await mock_task_manager.add_task("b task")
    await mock_task_manager.add_task("a task")
    await mock_task_manager.add_task("c task")

    async with app.run_test() as pilot:
        await select_sort_option(pilot, app, "Title ↓")

        assert app.sort_by == "title"
        assert app.sort_reverse is True
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item.data.title for item in tasks_list.children]
        assert rendered_tasks == ["c task", "b task", "a task"]


async def test_sort_modal_allows_selecting_each_option(app: LazyTaskApp):
    """
    The sort modal allows choosing any combination of field and direction.
    """
    async with app.run_test() as pilot:
        assert app.sort_by == "due_date"
        assert app.sort_reverse is False

        await select_sort_option(pilot, app, "Due date ↓")
        assert app.sort_by == "due_date"
        assert app.sort_reverse is True

        await select_sort_option(pilot, app, "Title ↑")
        assert app.sort_by == "title"
        assert app.sort_reverse is False

        await select_sort_option(pilot, app, "Creation date ↓")
        assert app.sort_by == "creation_date"
        assert app.sort_reverse is True


async def test_sort_by_title_case_insensitive(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that sorting by title is case-insensitive."""
    await mock_task_manager.add_task("b task")
    await mock_task_manager.add_task("a task")
    await mock_task_manager.add_task("C task")

    async with app.run_test() as pilot:
        await select_sort_option(pilot, app, "Title ↑")

        tasks_list = app.query_one("ListView")
        rendered_tasks = [item.data.title for item in tasks_list.children]
        assert rendered_tasks == ["a task", "b task", "C task"]


async def test_sort_by_creation_date(
    app: LazyTaskApp, mock_task_manager: MockTaskManager
):
    """Test that sorting by creation date works."""
    await mock_task_manager.add_task(
        "task 1", creation_date=datetime.datetime(2025, 1, 1, 12, 0, 2)
    )
    await mock_task_manager.add_task(
        "task 2", creation_date=datetime.datetime(2025, 1, 1, 12, 0, 1)
    )
    await mock_task_manager.add_task(
        "task 3", creation_date=datetime.datetime(2025, 1, 1, 12, 0, 3)
    )

    async with app.run_test() as pilot:
        await select_sort_option(pilot, app, "Creation date ↑")

        assert app.sort_by == "creation_date"
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item.data.title for item in tasks_list.children]
        assert rendered_tasks == ["task 2", "task 1", "task 3"]
