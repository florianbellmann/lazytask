import pytest
from unittest.mock import MagicMock, AsyncMock
import datetime

from lazytask.presentation.app import LazyTaskApp


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
