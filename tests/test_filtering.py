import pytest
from unittest.mock import MagicMock, AsyncMock

from lazytask.presentation.app import LazyTaskApp


import pytest

# ----------------------------
# Feature Tests: Filtering
# ----------------------------


@pytest.mark.skip(reason="Filtering via slash not implemented yet")
def test_filtering_with_slash_button():
    """
    Verify that pressing the slash button (`/`) activates filtering
    and allows typing a filter string.
    """
    # TODO: Implement filtering activation test
    pass


@pytest.mark.skip(reason="Case insensitive filtering not implemented yet")
def test_filtering_is_case_insensitive():
    """
    Verify that filtering matches tasks regardless of case.
    Example: typing 'foo' matches tasks named 'Foo' or 'FOO'.
    """
    # TODO: Implement case-insensitive filtering test
    pass


@pytest.mark.skip(reason="Filter persistence after task completion not implemented yet")
def test_filtering_persists_after_completing_task():
    """
    Verify that the active filter remains applied after a task is marked complete.
    """
    # TODO: Implement persistence after completion test
    pass


@pytest.mark.skip(reason="Filter persistence after adding task not implemented yet")
def test_filtering_persists_after_adding_task():
    """
    Verify that the active filter remains applied after adding a new task.
    """
    # TODO: Implement persistence after adding a task test
    pass


@pytest.mark.skip(reason="Escape key clearing filter not implemented yet")
def test_escape_clears_filtering():
    """
    Verify that pressing Escape clears the current filter text.
    """
    # TODO: Implement escape clearing filter test
    pass


@pytest.mark.skip(reason="Filter cleared when switching list not implemented yet")
def test_filtering_clears_when_switching_list():
    """
    Verify that switching to a different list clears the current filter.
    """
    # TODO: Implement filter clear on list switch test
    pass


@pytest.mark.skip(
    reason="Filter cleared when switching to all-list mode not implemented yet"
)
def test_filtering_clears_when_switching_to_all_list_mode():
    """
    Verify that switching to 'all lists' mode clears the current filter.
    """
    # TODO: Implement filter clear on all-list mode switch test
    pass


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
