import datetime

import pytest
from textual.widgets import Button

from lazytask.domain.task import Task
from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.date_picker_screen import DatePickerScreen


@pytest.fixture
def task() -> Task:
    return Task(id="1", title="Test Task", due_date=datetime.date(2025, 1, 1))


async def test_edit_due_date(task: Task):
    app = LazyTaskApp()
    async with app.run_test() as pilot:
        await app.push_screen(EditScreen(task))
        edit_screen = app.query_one(EditScreen)

        # Check that the initial due date is displayed correctly
        due_date_label = edit_screen.query_one("#due-date-label")
        assert str(task.due_date) in due_date_label.renderable

        # Click the "Edit Due Date" button
        edit_due_date_button = edit_screen.query_one("#edit-due-date", Button)
        await pilot.click(edit_due_date_button)
        await pilot.pause() # Wait for the screen to be pushed

        # Check that the DatePickerScreen is displayed
        date_picker_screen = app.query_one(DatePickerScreen)

        # Select a new date (e.g., today)
        new_date = datetime.date.today()
        date_picker_screen.dismiss(new_date)
        await pilot.pause()

        # Check that the due date label on the EditScreen is updated
        assert str(new_date) in due_date_label.renderable

        # Click the "Save" button
        save_button = edit_screen.query_one("#save", Button)
        await pilot.click(save_button)

        # Check that the task's due date has been updated
        assert task.due_date == new_date
