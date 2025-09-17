import pytest
from unittest.mock import MagicMock, AsyncMock

from lazytask.presentation.app import LazyTaskApp


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet")
async def test_filter_case_insensitive():
    """Test that filtering is case-insensitive."""
    # Given
    app = LazyTaskApp()
    app.use_case = MagicMock()
    app.use_case.get_tasks = AsyncMock(
        return_value=[
            {"id": "1", "title": "Task 1"},
            {"id": "2", "title": "task 2"},
            {"id": "3", "title": "TASK 3"},
        ]
    )
    app.query_one = MagicMock()

    # When
    await app.update_tasks_list(filter_query="task")

    # Then
    task_list = app.query_one.return_value
    assert task_list.add_task.call_count == 3


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet")
async def test_clear_filter_with_esc():
    """Test that pressing escape clears the filter."""
    # Given
    app = LazyTaskApp()
    app.use_case = MagicMock()
    app.use_case.get_tasks = AsyncMock(
        return_value=[
            {"id": "1", "title": "Task 1"},
            {"id": "2", "title": "task 2"},
            {"id": "3", "title": "TASK 3"},
        ]
    )
    app.query_one = MagicMock()
    await app.update_tasks_list(filter_query="task")
    task_list = app.query_one.return_value
    assert task_list.add_task.call_count == 3
    task_list.reset_mock()

    # When
    await app.action_clear_filter()

    # Then
    assert task_list.add_task.call_count == 3
