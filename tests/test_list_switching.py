import pytest
from unittest.mock import AsyncMock, MagicMock

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from textual.widgets import ListView


@pytest.mark.asyncio
async def test_switch_list_with_number_keys(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2,inbox,work")
    """Test that switching lists with number keys works."""
    app = LazyTaskApp()

    # Create mock use cases
    mock_get_lists_uc = MagicMock()
    mock_get_lists_uc.execute = AsyncMock(return_value=["inbox", "work"])

    mock_get_tasks_uc = MagicMock()
    inbox_task = Task(id="1", title="Task in inbox")
    work_task = Task(id="2", title="Task in work")
    develop_task = Task(id="3", title="Task in develop")
    develop2_task = Task(id="4", title="Task in develop2")

    async def get_tasks_side_effect(list_name, include_completed=False):
        if list_name == "all":
            return [inbox_task, work_task, develop_task, develop2_task]
        if list_name == "inbox":
            return [inbox_task]
        if list_name == "work":
            return [work_task]
        if list_name == "develop":
            return [develop_task]
        if list_name == "develop2":
            return [develop2_task]
        return []

    mock_get_tasks_uc.execute = AsyncMock(side_effect=get_tasks_side_effect)

    app.get_lists_uc = mock_get_lists_uc
    app.get_tasks_uc = mock_get_tasks_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        # Initially, it should be the default list
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop"

        # Initially, it should be the default list
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop"

        # Press '1' to switch to "All Tasks"
        await pilot.press("1")
        await pilot.pause()
        assert app.current_list == "all"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 4  # Assuming all tasks for "all" initially

        # Press '2' to switch to the first list 'develop'
        await pilot.press("2")
        await pilot.pause()
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop"

        # Press '3' to switch to the second list 'develop2'
        await pilot.press("3")
        await pilot.pause()
        assert app.current_list == "develop2"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in develop2"

        # Press '4' to switch to the third list 'inbox'
        await pilot.press("4")
        await pilot.pause()
        assert app.current_list == "inbox"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in inbox"

        # Press '5' to switch to the fourth list 'work'
        await pilot.press("5")
        await pilot.pause()
        assert app.current_list == "work"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 1
        assert list_view.children[0].data.title == "Task in work"


@pytest.mark.asyncio
async def test_list_switching_resets_index(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    """Test that switching lists resets the highlighted index to 0."""
    app = LazyTaskApp()

    mock_get_tasks_uc = MagicMock()
    develop_tasks = [Task(id=f"{i}", title=f"Task {i}") for i in range(5)]
    develop2_tasks = [Task(id=f"d2_{i}", title=f"Task d2 {i}") for i in range(3)]

    async def get_tasks_side_effect(list_name, include_completed=False):
        if list_name == "develop":
            return develop_tasks
        if list_name == "develop2":
            return develop2_tasks
        if list_name == "all":
            return develop_tasks + develop2_tasks
        return []

    mock_get_tasks_uc.execute = AsyncMock(side_effect=get_tasks_side_effect)
    app.get_tasks_uc = mock_get_tasks_uc

    async with app.run_test() as pilot:
        await pilot.pause()

        # Check that we are on the develop list
        assert app.current_list == "develop"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 5

        # Move down to the 3rd item (index 2)
        list_view.focus()
        await pilot.press("j")
        await pilot.press("j")
        await pilot.press("j")
        assert list_view.index == 2

        # Switch to the 'develop2' list
        await pilot.press("3")
        await pilot.pause()

        # Check that the index is reset to 0
        assert app.current_list == "develop2"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 3
        assert list_view.index == 0

        # Move down to the 2nd item (index 1)
        await pilot.press("j")
        assert list_view.index == 1

        # Switch to the 'all' view
        await pilot.press("1")
        await pilot.pause()

        # Check that the index is reset to 0
        assert app.current_list == "all"
        list_view = app.query_one(ListView)
        assert len(list_view.children) == 8
        assert list_view.index == 0


@pytest.mark.asyncio
async def test_switching_lists_resets_selection(monkeypatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")
    app = LazyTaskApp()

    mock_get_tasks_uc = MagicMock()
    develop_tasks = [Task(id=f"dev_{i}", title=f"Task {i}") for i in range(3)]
    develop2_tasks = [Task(id=f"d2_{i}", title=f"Task d2 {i}") for i in range(2)]

    async def get_tasks_side_effect(list_name, include_completed=False):
        if list_name == "develop":
            return develop_tasks
        if list_name == "develop2":
            return develop2_tasks
        if list_name == "all":
            return develop_tasks + develop2_tasks
        return []

    mock_get_tasks_uc.execute = AsyncMock(side_effect=get_tasks_side_effect)
    app.get_tasks_uc = mock_get_tasks_uc

    async with app.run_test() as pilot:
        await pilot.pause()
        list_view = app.query_one(ListView)

        # Initial state: develop list, 3 tasks
        assert app.current_list == "develop"
        assert len(list_view.children) == 3

        # Select the second task (index 1)
        list_view.index = 1
        await pilot.pause()
        assert list_view.index == 1

        # Switch to develop2 list
        await app.switch_list("develop2")
        await pilot.pause()

        # Check if index is reset to 0
        assert app.current_list == "develop2"
        assert len(list_view.children) == 2
        assert list_view.index == 0, "Index should be reset to 0 after switching list"

        # Select the last task (index 1)
        list_view.index = 1
        await pilot.pause()
        assert list_view.index == 1

        # Switch to all view
        await app.switch_list("all")
        await pilot.pause()

        # Check if index is reset to 0
        assert app.current_list == "all"
        assert len(list_view.children) == 5
        assert list_view.index == 0, (
            "Index should be reset to 0 after switching to all view"
        )
