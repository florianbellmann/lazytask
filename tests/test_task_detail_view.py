import datetime
from lazytask.presentation.app import LazyTaskApp
from lazytask.container import container


async def test_task_detail_shows_all_fields():
    """
    The TaskDetail widget should display all relevant fields of a Task.
    """
    app = LazyTaskApp()
    task_manager = container.task_manager
    task = await task_manager.add_task(
        title="Test Task",
        list_name="develop",
        due_date=datetime.date(2025, 1, 1),
        description="Test Description",
        tags=["tag1", "tag2"],
        priority=5,
        is_flagged=True,
        recurring="daily",
    )

    async with app.run_test() as pilot:
        await pilot.press("j")  # select the task
        await pilot.pause()

        task_detail = app.query_one("#task_detail")
        rendered_text = task_detail.renderable.text

        assert "Test Task" in rendered_text
        assert "List: develop" in rendered_text
        assert "Due Date: 2025-01-01" in rendered_text
        assert "Notes: Test Description" in rendered_text
        assert "Tags: tag1, tag2" in rendered_text
        assert "Priority: 5" in rendered_text
        assert "Flagged" in rendered_text
        assert "Recurring: daily" in rendered_text
        assert "Status: Pending" in rendered_text

        await task_manager.complete_task(task.id)
        app.show_completed = True
        await app.update_tasks_list()
        await pilot.pause()

        # after refresh, the selection is lost, so we need to select it again
        await pilot.press("j")
        await pilot.pause()

        rendered_text = task_detail.renderable.text
        assert "Status: Completed" in rendered_text
