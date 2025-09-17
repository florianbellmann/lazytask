import asyncio
import json
from typing import List, Optional, Dict, Any
from lazytask.domain.task_manager import TaskManager
from lazytask.domain.task import Task

import datetime

REMINDERS_CLI_PATH = (
    "/home/flo/lazytask/adapters/reminders-cli/reminders"  # Assuming binary is here
)


class RemindersCliTaskManager(TaskManager):
    async def _run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        process = await asyncio.create_subprocess_exec(
            REMINDERS_CLI_PATH,
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"CLI command failed with error: {stderr.decode().strip()}")

        output = stdout.decode().strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # Handle cases where output is not JSON (e.g., plain text messages)
                return {"message": output}
        return {}

    def _parse_reminder_json(self, reminder_json: Dict[str, Any]) -> Task:
        creation_date = None
        if reminder_json.get("creationDate"):
            try:
                creation_date = datetime.datetime.fromisoformat(
                    reminder_json.get("creationDate")
                )
            except (ValueError, TypeError):
                creation_date = None

        due_date = None
        if reminder_json.get("dueDate"):
            try:
                due_date = datetime.datetime.fromisoformat(
                    reminder_json.get("dueDate")
                ).date()
            except (ValueError, TypeError):
                due_date = None

        return Task(
            id=reminder_json.get("externalId"),
            title=reminder_json.get("title"),
            completed=reminder_json.get("isCompleted", False),
            due_date=due_date,
            creation_date=creation_date,
            list_name=reminder_json.get("list"),
            description=reminder_json.get("notes"),
            priority=reminder_json.get("priority"),
            is_flagged=False,  # reminders-cli doesn't support flags
            tags=[],  # reminders-cli doesn't support tags
        )

    async def add_task(self, title: str, list_name: str = "develop") -> Task:
        command = ["add", list_name, title, "--format", "json"]
        response = await self._run_cli_command(command)
        return self._parse_reminder_json(response)

    async def complete_task(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        command = ["complete", list_name, task_id]
        await self._run_cli_command(command)  # This command doesn't return JSON
        # To get the updated task, we need to fetch it
        # This is a limitation, as the CLI doesn't return the completed task
        # For now, we'll return None or try to fetch all tasks and find it
        # A better approach would be to modify the CLI to return the updated task
        return None  # Placeholder

    async def get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        command = ["show", list_name, "--format", "json"]
        if include_completed:
            command.extend(["--include-completed"])

        response = await self._run_cli_command(command)
        if isinstance(response, list):
            return [self._parse_reminder_json(r) for r in response]
        return []

    async def get_lists(self) -> List[str]:
        command = ["show-lists", "--format", "json"]
        response = await self._run_cli_command(command)
        if isinstance(response, list):
            return [str(item) for item in response]
        return []

    async def edit_task_date(
        self, task_id: str, new_date: str, list_name: str = "develop"
    ) -> Optional[Task]:
        # This is a workaround as reminders-cli edit doesn't support due date directly
        # Fetch the task, delete it, and re-add with new date
        # This is not atomic and can lead to data loss if re-add fails
        # A better solution would require modifying the reminders-cli
        tasks = await self.get_tasks(list_name, include_completed=True)
        original_task = next((t for t in tasks if t.id == task_id), None)

        if original_task:
            await self._run_cli_command(["delete", list_name, task_id])
            # Re-add with new date and original properties
            command = ["add", list_name, original_task.title, "--format", "json"]
            if new_date:  # Assuming new_date is in a format reminders-cli understands (e.g., YYYY-MM-DD)
                command.extend(["--due-date", new_date])
            if original_task.description:
                command.extend(["--notes", original_task.description])
            if original_task.priority is not None:
                command.extend(["--priority", str(original_task.priority)])

            new_task_json = await self._run_cli_command(command)
            return self._parse_reminder_json(new_task_json)
        return None

    async def move_task_to_tomorrow(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        # Similar workaround as edit_task_date
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        return await self.edit_task_date(task_id, tomorrow, list_name)

    async def edit_task_description(
        self, task_id: str, description: str, list_name: str = "develop"
    ) -> Optional[Task]:
        command = ["edit", list_name, task_id, "--notes", description]
        await self._run_cli_command(command)
        # The CLI doesn't return the updated task, so we fetch it
        tasks = await self.get_tasks(list_name, include_completed=True)
        return next((t for t in tasks if t.id == task_id), None)

    async def edit_task_tags(
        self, task_id: str, tags: List[str], list_name: str = "develop"
    ) -> Optional[Task]:
        # Tags are not directly supported by reminders-cli
        # We could potentially append tags to the notes, but that's a design decision
        # For now, we'll treat this as unsupported.
        print("Warning: Editing tags is not directly supported by reminders-cli.")
        return None

    async def edit_task_priority(
        self, task_id: str, priority: int, list_name: str = "develop"
    ) -> Optional[Task]:
        # Similar workaround as edit_task_date
        tasks = await self.get_tasks(list_name, include_completed=True)
        original_task = next((t for t in tasks if t.id == task_id), None)

        if original_task:
            await self._run_cli_command(["delete", list_name, task_id])
            command = ["add", list_name, original_task.title, "--format", "json"]
            if original_task.due_date:
                command.extend(["--due-date", original_task.due_date])
            if original_task.description:
                command.extend(["--notes", original_task.description])
            command.extend(["--priority", str(priority)])

            new_task_json = await self._run_cli_command(command)
            return self._parse_reminder_json(new_task_json)
        return None

    async def edit_task_flag(
        self, task_id: str, flagged: bool, list_name: str = "develop"
    ) -> Optional[Task]:
        # Flags are not directly supported by reminders-cli
        print("Warning: Editing flags is not directly supported by reminders-cli.")
        return None

    async def refresh_tasks(self, list_name: str = "develop") -> List[Task]:
        return await self.get_tasks(list_name)

    async def filter_tasks(
        self,
        list_name: str = "develop",
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[int] = None,
        flagged: Optional[bool] = None,
        include_completed: bool = False,
    ) -> List[Task]:
        # Fetch all relevant tasks and then filter in Python
        tasks = await self.get_tasks(list_name, include_completed=True)
        filtered_tasks = []
        for task in tasks:
            match = True
            if (
                query
                and query.lower() not in task.title.lower()
                and (task.description and query.lower() not in task.description.lower())
            ):
                match = False
            # Tags and flagged are not supported by CLI, so filtering on them here is moot
            # unless we decide to parse them from notes/title, which is not implemented yet.
            if priority is not None and task.priority != priority:
                match = False
            if (
                flagged is not None and task.flagged != flagged
            ):  # This will always be False as flagged is hardcoded
                match = False
            if match:
                filtered_tasks.append(task)
        return filtered_tasks

    async def sort_tasks(
        self, list_name: str = "develop", sort_by: str = "due_date"
    ) -> List[Task]:
        # Fetch all relevant tasks and then sort in Python
        tasks = await self.get_tasks(list_name, include_completed=True)
        if sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date if t.due_date else "9999-12-31")
        elif sort_by == "title":
            tasks.sort(key=lambda t: t.title.lower())
        elif sort_by == "priority":
            tasks.sort(key=lambda t: t.priority if t.priority is not None else 999)
        elif sort_by == "completed":
            tasks.sort(key=lambda t: t.completed)
        return tasks

    async def edit_task_full(
        self, task_id: str, updates: Dict[str, Any], list_name: str = "develop"
    ) -> Optional[Task]:
        # This is a workaround as reminders-cli edit doesn't support all fields
        # We will call the specific edit methods for each field
        task = None
        if "title" in updates:
            # Not supported by reminders-cli
            pass
        if "due_date" in updates:
            task = await self.edit_task_date(task_id, updates["due_date"], list_name)
        if "description" in updates:
            task = await self.edit_task_description(
                task_id, updates["description"], list_name
            )
        if "priority" in updates:
            task = await self.edit_task_priority(
                task_id, updates["priority"], list_name
            )
        if "tags" in updates:
            task = await self.edit_task_tags(task_id, updates["tags"], list_name)
        if "is_flagged" in updates:
            task = await self.edit_task_flag(task_id, updates["is_flagged"], list_name)
        if "recurring" in updates:
            task = await self.set_task_recurring(
                task_id, updates["recurring"], list_name
            )

        return task

    async def set_task_recurring(
        self, task_id: str, recurring: str, list_name: str = "develop"
    ) -> Optional[Task]:
        # Recurring tasks are not supported by reminders-cli
        print("Warning: Setting recurring tasks is not supported by reminders-cli.")
        return None
