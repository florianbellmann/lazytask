import datetime
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


async def test_default_sort_due_date_oldest_first_selected_on_startup():
    """
    On startup:
      - The selected sort is 'due date ascending' (oldest first).
      - The visible list is sorted by due date from oldest to newest.
    """
    app = LazyTaskApp()
    assert app.sort_by == "due_date"
    assert app.sort_reverse is False

    task_manager = container.task_manager
    await task_manager.add_task("task 1", due_date=datetime.date(2025, 1, 2))
    await task_manager.add_task("task 2", due_date=datetime.date(2025, 1, 1))
    await task_manager.add_task("task 3", due_date=datetime.date(2025, 1, 3))

    async with app.run_test() as pilot:
        await pilot.pause()
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item._task.title for item in tasks_list.children]
        assert rendered_tasks == ["task 2", "task 1", "task 3"]


async def test_sort_due_date_descending_when_direction_reversed():
    """
    When switching the sort direction while on 'due date':
      - The list becomes sorted newest -> oldest.
      - Confirm it is strictly the reverse order of ascending-by-due-date.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("task 1", due_date=datetime.date(2025, 1, 2))
    await task_manager.add_task("task 2", due_date=datetime.date(2025, 1, 1))
    await task_manager.add_task("task 3", due_date=datetime.date(2025, 1, 3))

    async with app.run_test() as pilot:
        await pilot.press("ctrl+i")  # reverse sort
        await pilot.pause()

        assert app.sort_reverse is True
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item._task.title for item in tasks_list.children]
        assert rendered_tasks == ["task 3", "task 1", "task 2"]


async def test_sort_alphabetically_ascending():
    """
    When choosing alphabetical sort:
      - The list is sorted A -> Z by task title.
      - The selected sort reflects 'alphabetical ascending'.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("b task")
    await task_manager.add_task("a task")
    await task_manager.add_task("c task")

    async with app.run_test() as pilot:
        # Default sort is by due_date. Press ctrl+o to switch to title sort.
        await pilot.press("ctrl+o")
        await pilot.pause()

        assert app.sort_by == "title"
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item._task.title for item in tasks_list.children]
        assert rendered_tasks == ["a task", "b task", "c task"]


async def test_sort_alphabetically_descending():
    """
    When choosing alphabetical sort reversed:
      - The list is sorted Z -> A by task title.
      - Confirm it is strictly the reverse order of alphabetical ascending.
      - The selected sort reflects 'alphabetical descending'.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("b task")
    await task_manager.add_task("a task")
    await task_manager.add_task("c task")

    async with app.run_test() as pilot:
        await pilot.press("ctrl+o")  # sort by title
        await pilot.press("ctrl+i")  # reverse sort
        await pilot.pause()

        assert app.sort_by == "title"
        assert app.sort_reverse is True
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item._task.title for item in tasks_list.children]
        assert rendered_tasks == ["c task", "b task", "a task"]


async def test_sort_cycle():
    """
    Choosing sort cycles through due_date, title, creation_date.
    """
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        assert app.sort_by == "due_date"

        await pilot.press("ctrl+o")
        await pilot.pause()
        assert app.sort_by == "title"

        await pilot.press("ctrl+o")
        await pilot.pause()
        assert app.sort_by == "creation_date"

        await pilot.press("ctrl+o")
        await pilot.pause()
        assert app.sort_by == "due_date"


async def test_sort_by_title_case_insensitive():
    """Test that sorting by title is case-insensitive."""
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task("b task")
    await task_manager.add_task("a task")
    await task_manager.add_task("C task")

    async with app.run_test() as pilot:
        await pilot.press("ctrl+o")  # sort by title
        await pilot.pause()

        tasks_list = app.query_one("ListView")
        rendered_tasks = [item._task.title for item in tasks_list.children]
        assert rendered_tasks == ["a task", "b task", "C task"]


async def test_sort_by_creation_date():
    """Test that sorting by creation date works."""
    app = LazyTaskApp()
    task_manager = container.task_manager
    await task_manager.add_task(
        "task 1", creation_date=datetime.datetime(2025, 1, 1, 12, 0, 2)
    )
    await task_manager.add_task(
        "task 2", creation_date=datetime.datetime(2025, 1, 1, 12, 0, 1)
    )
    await task_manager.add_task(
        "task 3", creation_date=datetime.datetime(2025, 1, 1, 12, 0, 3)
    )

    async with app.run_test() as pilot:
        await pilot.press("ctrl+o")  # sort by title
        await pilot.press("ctrl+o")  # sort by creation_date
        await pilot.pause()

        assert app.sort_by == "creation_date"
        tasks_list = app.query_one("ListView")
        rendered_tasks = [item._task.title for item in tasks_list.children]
        assert rendered_tasks == ["task 2", "task 1", "task 3"]
