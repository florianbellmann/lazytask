import pytest
import datetime
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture
def task_manager(tmp_path):
    file_path = tmp_path / "test_tasks.json"
    return MockTaskManager(file_path=str(file_path))


@pytest.mark.asyncio
async def test_add_task(task_manager):
    title = "Test Task"
    task = await task_manager.add_task(title)
    assert task.title == title
    tasks = await task_manager.get_tasks()
    assert len(tasks) == 1


@pytest.mark.asyncio
async def test_complete_task(task_manager):
    title = "Test Task"
    task = await task_manager.add_task(title)
    completed_task = await task_manager.complete_task(task.id)
    assert completed_task.completed is True


@pytest.mark.asyncio
async def test_get_tasks(task_manager):
    await task_manager.add_task("Task 1")
    await task_manager.add_task("Task 2")
    tasks = await task_manager.get_tasks()
    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_get_lists(task_manager):
    lists = await task_manager.get_lists()
    assert "develop" in lists


@pytest.mark.asyncio
async def test_edit_task_date(task_manager):
    task = await task_manager.add_task("Test Task")
    new_date = "2025-12-31"
    updated_task = await task_manager.edit_task_date(task.id, new_date)
    assert (
        updated_task.due_date == datetime.datetime.strptime(new_date, "%Y-%m-%d").date()
    )


@pytest.mark.asyncio
async def test_move_task_to_tomorrow(task_manager):
    task = await task_manager.add_task("Test Task")
    updated_task = await task_manager.move_task_to_tomorrow(task.id)
    import datetime

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    assert updated_task.due_date == tomorrow


@pytest.mark.asyncio
async def test_edit_task_description(task_manager):
    task = await task_manager.add_task("Test Task")
    new_description = "This is a test description"
    updated_task = await task_manager.edit_task_description(task.id, new_description)
    assert updated_task.description == new_description


@pytest.mark.asyncio
async def test_edit_task_tags(task_manager):
    task = await task_manager.add_task("Test Task")
    new_tags = ["tag1", "tag2"]
    updated_task = await task_manager.edit_task_tags(task.id, new_tags)
    assert updated_task.tags == new_tags


@pytest.mark.asyncio
async def test_edit_task_priority(task_manager):
    task = await task_manager.add_task("Test Task")
    new_priority = 1
    updated_task = await task_manager.edit_task_priority(task.id, new_priority)
    assert updated_task.priority == new_priority


@pytest.mark.asyncio
async def test_edit_task_flag(task_manager):
    task = await task_manager.add_task("Test Task")
    updated_task = await task_manager.edit_task_flag(task.id, True)
    assert updated_task.is_flagged is True


@pytest.mark.asyncio
async def test_filter_tasks(task_manager):
    await task_manager.add_task("Task 1", priority=1)
    await task_manager.add_task("Task 2", priority=2)
    filtered_tasks = await task_manager.filter_tasks(priority=1)
    assert len(filtered_tasks) == 1
    assert filtered_tasks[0].priority == 1


@pytest.mark.asyncio
async def test_sort_tasks(task_manager):
    await task_manager.add_task("B Task")
    await task_manager.add_task("A Task")
    sorted_tasks = await task_manager.sort_tasks(sort_by="title")
    assert sorted_tasks[0].title == "A Task"
    assert sorted_tasks[1].title == "B Task"


@pytest.mark.asyncio
async def test_edit_task_full(task_manager):
    task = await task_manager.add_task("Test Task")
    updates = {"title": "New Title", "description": "New Description", "priority": 1}
    updated_task = await task_manager.edit_task_full(task.id, updates)
    assert updated_task.title == "New Title"
    assert updated_task.description == "New Description"
    assert updated_task.priority == 1


@pytest.mark.asyncio
async def test_set_task_recurring(task_manager):
    task = await task_manager.add_task("Test Task")
    updated_task = await task_manager.set_task_recurring(task.id, "daily")
    assert updated_task.recurring == "daily"
