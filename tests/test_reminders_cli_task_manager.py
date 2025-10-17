import datetime
from typing import Any, Dict, List

import pytest

from lazytask.domain.task import Task
from lazytask.infrastructure.reminders_cli_task_manager import (
    RemindersCliTaskManager,
)


@pytest.mark.asyncio
async def test_reminders_cli_move_task_recreates_and_deletes(monkeypatch: pytest.MonkeyPatch):
    manager = RemindersCliTaskManager()

    source_task = Task(
        id="source-id",
        title="Test Task",
        list_name="develop",
        description="Details",
        due_date=datetime.date(2024, 8, 20),
        priority=5,
        completed=False,
    )

    observations: Dict[str, Any] = {"get_tasks": [], "add_task": [], "delete": []}

    async def fake_get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        observations["get_tasks"].append((list_name, include_completed))
        return [source_task]

    async def fake_add_task(
        self, title: str, list_name: str = "develop", **kwargs: Any
    ) -> Task:
        observations["add_task"].append((title, list_name, dict(kwargs)))
        due_date_value = kwargs.get("due_date")
        if isinstance(due_date_value, str):
            due_date_value = datetime.datetime.strptime(
                due_date_value, "%Y-%m-%d"
            ).date()
        return Task(
            id="new-id",
            title=title,
            list_name=list_name,
            description=kwargs.get("description"),
            due_date=due_date_value,
            priority=kwargs.get("priority"),
            completed=False,
        )

    async def fake_run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        observations["delete"].append(command)
        return {}

    monkeypatch.setattr(RemindersCliTaskManager, "get_tasks", fake_get_tasks)
    monkeypatch.setattr(RemindersCliTaskManager, "add_task", fake_add_task)
    monkeypatch.setattr(
        RemindersCliTaskManager,
        "_run_cli_command",
        fake_run_cli_command,
    )

    moved_task = await manager.move_task("source-id", "develop", "develop2")

    observations["result"] = (
        moved_task.id,
        moved_task.title,
        moved_task.list_name,
        moved_task.due_date,
        moved_task.description,
        moved_task.priority,
    )

    expected: Dict[str, Any] = {
        "get_tasks": [("develop", True)],
        "add_task": [
            (
                "Test Task",
                "develop2",
                {
                    "description": "Details",
                    "due_date": datetime.date(2024, 8, 20),
                    "priority": 5,
                },
            )
        ],
        "delete": [["delete", "develop", "source-id"]],
        "result": (
            "new-id",
            "Test Task",
            "develop2",
            datetime.date(2024, 8, 20),
            "Details",
            5,
        ),
    }

    assert observations == expected


@pytest.mark.asyncio
async def test_reminders_cli_move_task_rejects_completed_tasks(monkeypatch: pytest.MonkeyPatch):
    manager = RemindersCliTaskManager()
    completed_task = Task(
        id="completed-id",
        title="Completed Task",
        list_name="develop",
        completed=True,
    )

    async def fake_get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        return [completed_task]

    monkeypatch.setattr(RemindersCliTaskManager, "get_tasks", fake_get_tasks)

    with pytest.raises(
        RuntimeError,
        match="Completed task 'completed-id' cannot be moved from 'develop'",
    ):
        await manager.move_task("completed-id", "develop", "develop2")


@pytest.mark.asyncio
async def test_reminders_cli_edit_task_date_recreates_and_deletes(monkeypatch: pytest.MonkeyPatch):
    manager = RemindersCliTaskManager()
    original_task = Task(
        id="task-id",
        title="Due Soon",
        list_name="develop",
        description="Check deadline",
        due_date=datetime.date(2024, 8, 20),
        priority=1,
        completed=False,
    )

    observations: Dict[str, Any] = {"get_tasks": [], "add_task": [], "delete": []}

    async def fake_get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        observations["get_tasks"].append((list_name, include_completed))
        return [original_task]

    async def fake_add_task(
        self, title: str, list_name: str = "develop", **kwargs: Any
    ) -> Task:
        observations["add_task"].append((title, list_name, dict(kwargs)))
        due_date_value = kwargs.get("due_date")
        if isinstance(due_date_value, str):
            due_date_value = datetime.datetime.strptime(
                due_date_value, "%Y-%m-%d"
            ).date()
        return Task(
            id="new-id",
            title=title,
            list_name=list_name,
            description=kwargs.get("description"),
            due_date=due_date_value,
            priority=kwargs.get("priority"),
            completed=False,
        )

    async def fake_run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        observations["delete"].append(command)
        return {}

    monkeypatch.setattr(RemindersCliTaskManager, "get_tasks", fake_get_tasks)
    monkeypatch.setattr(RemindersCliTaskManager, "add_task", fake_add_task)
    monkeypatch.setattr(
        RemindersCliTaskManager,
        "_run_cli_command",
        fake_run_cli_command,
    )

    new_due_date = datetime.date(2024, 9, 1)
    updated_task = await manager.edit_task_date("task-id", new_due_date, "develop")

    observations["result"] = (
        updated_task.id,
        updated_task.list_name,
        updated_task.due_date,
        updated_task.description,
        updated_task.priority,
    )

    expected: Dict[str, Any] = {
        "get_tasks": [("develop", True)],
        "add_task": [
            (
                "Due Soon",
                "develop",
                {
                    "due_date": "2024-09-01",
                    "description": "Check deadline",
                    "priority": 1,
                },
            )
        ],
        "delete": [["delete", "develop", "task-id"]],
        "result": ("new-id", "develop", datetime.date(2024, 9, 1), "Check deadline", 1),
    }

    assert observations == expected


@pytest.mark.asyncio
async def test_reminders_cli_edit_task_date_aborts_on_add_failure(monkeypatch: pytest.MonkeyPatch):
    manager = RemindersCliTaskManager()
    original_task = Task(
        id="task-id",
        title="Due Soon",
        list_name="develop",
        description="Check deadline",
        due_date=datetime.date(2024, 8, 20),
        priority=1,
        completed=False,
    )

    async def fake_get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        return [original_task]

    async def failing_add_task(
        self, title: str, list_name: str = "develop", **kwargs: Any
    ) -> Task:
        raise RuntimeError("Simulated add failure")

    async def fake_run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        pytest.fail("Delete should not run when add_task fails")

    monkeypatch.setattr(RemindersCliTaskManager, "get_tasks", fake_get_tasks)
    monkeypatch.setattr(RemindersCliTaskManager, "add_task", failing_add_task)
    monkeypatch.setattr(
        RemindersCliTaskManager,
        "_run_cli_command",
        fake_run_cli_command,
    )

    with pytest.raises(
        RuntimeError,
        match="Failed to create task 'Due Soon' on 'develop' while updating the due date.",
    ):
        await manager.edit_task_date(
            "task-id", datetime.date(2024, 9, 1), "develop"
        )


@pytest.mark.asyncio
async def test_reminders_cli_edit_task_date_rejects_completed_tasks(monkeypatch: pytest.MonkeyPatch):
    manager = RemindersCliTaskManager()
    completed_task = Task(
        id="task-id",
        title="Already Done",
        list_name="develop",
        completed=True,
    )

    async def fake_get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        return [completed_task]

    monkeypatch.setattr(RemindersCliTaskManager, "get_tasks", fake_get_tasks)

    with pytest.raises(
        RuntimeError,
        match="Completed task 'task-id' cannot be rescheduled on 'develop'.",
    ):
        await manager.edit_task_date("task-id", datetime.date.today(), "develop")
