import datetime

import pytest

from lazytask.presentation.app import LazyTaskApp
from lazytask.presentation.edit_screen import EditScreen
from lazytask.presentation.date_picker_screen import DatePickerScreen
from lazytask.infrastructure.mock_task_manager import MockTaskManager


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LAZYTASK_LISTS", "develop,develop2")



