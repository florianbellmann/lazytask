
import json
import asyncio
import datetime
from typing import List, Optional

from lazytask.domain.repository import TaskRepository
from lazytask.domain.task import Task

class RemindersTaskRepository(TaskRepository):
    def __init__(self, reminders_cli_path: str = "reminders") -> None:
        self.cli_path = reminders_cli_path
        self._current_list = "develop"

    async def _run_command(self, *args) -> dict:
        command = [self.cli_path, *args]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"Error running reminders-cli: {stderr.decode()}")

        if "--format" in args and "json" in args:
            return json.loads(stdout.decode())
        return {}

    async def get_all_tasks(self) -> List[Task]:
        tasks_json = await self._run_command("show", self._current_list, "--format", "json")
        tasks = []
        for task_json in tasks_json:
            tasks.append(self._json_to_task(task_json))
        return tasks

    def _json_to_task(self, json_data: dict) -> Task:
        due_date_str = json_data.get("dueDate")
        due_date = None
        if due_date_str:
            due_date = datetime.datetime.fromisoformat(due_date_str).date()

        return Task(
            id=json_data.get("externalId"),
            title=json_data.get("title"),
            completed=json_data.get("isCompleted", False),
            due_date=due_date,
            description=json_data.get("notes"),
            priority=json_data.get("priority"),
        )

    async def add_task(self, title: str) -> Task:
        task_json = await self._run_command("add", self._current_list, title, "--format", "json")
        return self._json_to_task(task_json)

    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        tasks = await self.get_all_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    async def complete_task(self, task_id: str) -> None:
        await self._run_command("complete", self._current_list, task_id)

    async def update_task(self, task: Task) -> None:
        args = ["edit", self._current_list, task.id]
        if task.title:
            args.append(task.title)
        if task.description:
            args.extend(["--notes", task.description])
        # The CLI does not support updating other fields like due date, priority etc.
        # This is a limitation of the current implementation.
        await self._run_command(*args)

    def switch_list(self, list_name: str) -> None:
        self._current_list = list_name
