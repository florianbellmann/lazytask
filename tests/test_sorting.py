import pytest
from unittest.mock import MagicMock, AsyncMock
import datetime

from lazytask.presentation.app import LazyTaskApp


import pytest

# ----------------------------
# Feature Tests: Sorting
# ----------------------------

@pytest.mark.skip(reason="Default sort not implemented yet")
def test_default_sort_due_date_oldest_first_selected_on_startup():
    """
    On startup:
      - The selected sort is 'due date ascending' (oldest first).
      - The visible list is sorted by due date from oldest to newest.
    """
    # TODO: Implement startup/default sort verification
    pass


@pytest.mark.skip(reason="Sort direction toggle not implemented yet")
def test_sort_due_date_descending_when_direction_reversed():
    """
    When switching the sort direction while on 'due date':
      - The list becomes sorted newest -> oldest.
      - Confirm it is strictly the reverse order of ascending-by-due-date.
    """
    # TODO: Implement direction toggle verification for due date
    pass


@pytest.mark.skip(reason="Alphabetical ascending sort not implemented yet")
def test_sort_alphabetically_ascending():
    """
    When choosing alphabetical sort:
      - The list is sorted A -> Z by task title.
      - The selected sort reflects 'alphabetical ascending'.
    """
    # TODO: Implement alphabetical ascending verification
    pass


@pytest.mark.skip(reason="Alphabetical descending sort not implemented yet")
def test_sort_alphabetically_descending():
    """
    When choosing alphabetical sort reversed:
      - The list is sorted Z -> A by task title.
      - Confirm it is strictly the reverse order of alphabetical ascending.
      - The selected sort reflects 'alphabetical descending'.
    """
    # TODO: Implement alphabetical descending verification
    pass


@pytest.mark.skip(reason="Alphabetical selection state not implemented yet")
def test_selecting_alphabetical_updates_selected_sort():
    """
    Choosing alphabetical again (from any prior sort) sets the selected sort to 'alphabetical'
    and displays the list accordingly (default direction A -> Z).
    """
    # TODO: Implement selected-sort state update check when choosing alphabetical
    pass



@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet")
async def test_sort_by_title_case_insensitive():
    """Test that sorting by title is case-insensitive."""
    # Given
    app = LazyTaskApp()
    app.use_case = MagicMock()
    app.use_case.get_tasks = AsyncMock(
        return_value=[
            {"id": "1", "title": "b"},
            {"id": "2", "title": "a"},
            {"id": "3", "title": "C"},
        ]
    )
    app.query_one = MagicMock()
    app.sort_by = "title"

    # When
    await app.update_tasks_list()

    # Then
    task_list = app.query_one.return_value
    assert task_list.add_task.call_args_list[0].args[0].title == "a"
    assert task_list.add_task.call_args_list[1].args[0].title == "b"
    assert task_list.add_task.call_args_list[2].args[0].title == "C"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet")
async def test_sort_by_creation_date():
    """Test that sorting by creation date works."""
    # Given
    app = LazyTaskApp()
    app.use_case = MagicMock()
    app.use_case.get_tasks = AsyncMock(
        return_value=[
            {"id": "1", "title": "b", "creation_date": datetime.datetime(2023, 1, 2)},
            {"id": "2", "title": "a", "creation_date": datetime.datetime(2023, 1, 1)},
            {"id": "3", "title": "C", "creation_date": datetime.datetime(2023, 1, 3)},
        ]
    )
    app.query_one = MagicMock()
    app.sort_by = "creation_date"

    # When
    await app.update_tasks_list()

    # Then
    task_list = app.query_one.return_value
    assert task_list.add_task.call_args_list[0].args[0].title == "a"
    assert task_list.add_task.call_args_list[1].args[0].title == "b"
    assert task_list.add_task.call_args_list[2].args[0].title == "C"
