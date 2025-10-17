import asyncio
import json
from typing import List, Optional, Dict, Any
from lazytask.domain.task_manager import TaskManager
from lazytask.domain.task import Task

import datetime

REMINDERS_CLI_PATH = "adapters/reminders-cli/reminders"  # Assuming binary is here


class RemindersCliTaskManager(TaskManager):
    _PRIORITY_INT_TO_CLI_NAME = {
        0: "none",
        1: "high",
        2: "medium",
        3: "low",
        5: "medium",
        9: "low",
    }
    _PRIORITY_NAME_SET = {"none", "low", "medium", "high"}

    @staticmethod
    def _parse_cli_datetime(value: str | None) -> Optional[datetime.datetime]:
        if not value:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            return datetime.datetime.fromisoformat(normalized)
        except ValueError:
            return None

    @staticmethod
    def _parse_cli_date(value: str | None) -> Optional[datetime.date]:
        if not value:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            return datetime.datetime.fromisoformat(normalized).date()
        except ValueError:
            try:
                return datetime.datetime.strptime(normalized, "%Y-%m-%d").date()
            except ValueError:
                return None

    def _due_date_to_cli_value(self, due_date: Any) -> Optional[str]:
        if due_date is None:
            return None

        if isinstance(due_date, datetime.datetime):
            return due_date.isoformat()

        if isinstance(due_date, datetime.date):
            return due_date.isoformat()

        if isinstance(due_date, str):
            candidate = due_date.strip()
            if not candidate:
                raise ValueError("Due date string cannot be empty.")
            return candidate

        raise ValueError(
            f"Unsupported due date type '{type(due_date).__name__}'. "
            "Use datetime.date, datetime.datetime, or ISO-8601 string inputs."
        )

    def _priority_to_cli_value(self, priority: Any) -> Optional[str]:
        if priority is None:
            return None

        if isinstance(priority, str):
            normalized_priority = priority.strip().lower()
            if normalized_priority in self._PRIORITY_NAME_SET:
                return normalized_priority
            if normalized_priority.isdigit():
                priority = int(normalized_priority)
            else:
                raise ValueError(
                    f"Unsupported priority value '{priority}'. "
                    f"Expected one of {sorted(self._PRIORITY_NAME_SET)} or numeric values {sorted(self._PRIORITY_INT_TO_CLI_NAME)}."
                )

        try:
            priority_value = int(priority)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Unsupported priority type '{priority}'. Unable to convert to reminders-cli priority."
            ) from error

        if priority_value in self._PRIORITY_INT_TO_CLI_NAME:
            return self._PRIORITY_INT_TO_CLI_NAME[priority_value]

        raise ValueError(
            f"Unsupported numeric priority '{priority_value}'. "
            f"Supported values: {sorted(self._PRIORITY_INT_TO_CLI_NAME)}."
        )

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
        creation_date_str = reminder_json.get("creationDate")
        if creation_date_str:
            creation_date = self._parse_cli_datetime(creation_date_str)

        due_date = None
        due_date_str = reminder_json.get("dueDate")
        if due_date_str:
            due_date = self._parse_cli_date(due_date_str)

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

    def _normalize_list_name(self, list_name: str) -> str:
        cleaned = (list_name or "").strip()
        if not cleaned:
            raise ValueError("List name must not be empty")
        return cleaned

    async def add_task(
        self, title: str, list_name: str = "develop", **kwargs: Any
    ) -> Task:
        clean_list = self._normalize_list_name(list_name)
        command = ["add", clean_list, title, "--format", "json"]

        due_date = kwargs.get("due_date")
        if due_date:
            try:
                due_date_argument = self._due_date_to_cli_value(due_date)
                if due_date_argument:
                    command.extend(["--due-date", due_date_argument])
            except ValueError as error:
                raise ValueError(
                    f"Invalid due date '{due_date}' while adding task '{title}' to '{clean_list}'."
                ) from error

        description = kwargs.get("description")
        if description:
            command.extend(["--notes", description])

        priority = kwargs.get("priority")
        if priority is not None:
            try:
                priority_argument = self._priority_to_cli_value(priority)
                if priority_argument:
                    command.extend(["--priority", priority_argument])
            except ValueError as error:
                raise ValueError(
                    f"Invalid priority '{priority}' while adding task '{title}' to '{clean_list}'."
                ) from error

        response = await self._run_cli_command(command)
        return self._parse_reminder_json(response)

    async def complete_task(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        clean_list = self._normalize_list_name(list_name)
        command = ["complete", clean_list, task_id]
        await self._run_cli_command(command)  # This command doesn't return JSON
        # To get the updated task, we need to fetch it
        # This is a limitation, as the CLI doesn't return the completed task
        # For now, we'll return None or try to fetch all tasks and find it
        # A better approach would be to modify the CLI to return the updated task
        return None  # Placeholder

    async def get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        clean_list = self._normalize_list_name(list_name)
        command = ["show", clean_list, "--format", "json"]
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
            trimmed_lists = []
            for item in response:
                cleaned = str(item).strip()
                if cleaned:
                    trimmed_lists.append(cleaned)
            return trimmed_lists
        return []

    async def edit_task_date(
        self,
        task_id: str,
        new_date: datetime.date | datetime.datetime | str | None,
        list_name: str = "develop",
    ) -> Optional[Task]:
        clean_list = self._normalize_list_name(list_name)
        tasks = await self.get_tasks(clean_list, include_completed=True)
        original_task = next((t for t in tasks if t.id == task_id), None)

        if not original_task:
            return None

        if original_task.completed:
            raise RuntimeError(
                f"Completed task '{task_id}' cannot be rescheduled on '{clean_list}'. "
                "Mark it as incomplete first."
            )

        recreation_kwargs: Dict[str, Any] = {}
        if new_date is not None:
            try:
                recreation_kwargs["due_date"] = self._due_date_to_cli_value(new_date)
            except ValueError as error:
                raise ValueError(
                    f"Invalid due date '{new_date}' for task '{task_id}' on '{clean_list}'."
                ) from error
        if original_task.description:
            recreation_kwargs["description"] = original_task.description
        if original_task.priority is not None:
            recreation_kwargs["priority"] = original_task.priority

        try:
            recreated_task = await self.add_task(
                original_task.title,
                list_name=clean_list,
                **recreation_kwargs,
            )
        except Exception as error:
            raise RuntimeError(
                f"Failed to create task '{original_task.title}' on '{clean_list}' "
                "while updating the due date."
            ) from error

        try:
            await self._run_cli_command(["delete", clean_list, task_id])
        except Exception as error:
            cleanup_error: Optional[Exception] = None
            try:
                await self._run_cli_command(["delete", clean_list, recreated_task.id])
            except Exception as attempted_cleanup_error:
                cleanup_error = attempted_cleanup_error

            if cleanup_error:
                raise RuntimeError(
                    f"Failed to delete original task '{task_id}' from '{clean_list}' "
                    f"and rollback of recreated task '{recreated_task.id}' also failed."
                ) from error

            raise RuntimeError(
                f"Failed to delete original task '{task_id}' from '{clean_list}' "
                "after recreating it with a new due date."
            ) from error

        return recreated_task

    async def move_task_to_tomorrow(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        # Similar workaround as edit_task_date
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        return await self.edit_task_date(task_id, tomorrow, list_name)

    async def edit_task_description(
        self, task_id: str, description: str, list_name: str = "develop"
    ) -> Optional[Task]:
        clean_list = self._normalize_list_name(list_name)
        command = ["edit", clean_list, task_id, "--notes", description]
        await self._run_cli_command(command)
        # The CLI doesn't return the updated task, so we fetch it
        tasks = await self.get_tasks(clean_list, include_completed=True)
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
        clean_list = self._normalize_list_name(list_name)
        tasks = await self.get_tasks(clean_list, include_completed=True)
        original_task = next((t for t in tasks if t.id == task_id), None)

        if original_task:
            await self._run_cli_command(["delete", clean_list, task_id])
            command = ["add", clean_list, original_task.title, "--format", "json"]
            if original_task.due_date:
                due_date_argument = self._due_date_to_cli_value(original_task.due_date)
                if due_date_argument:
                    command.extend(["--due-date", due_date_argument])
            if original_task.description:
                command.extend(["--notes", original_task.description])
            try:
                priority_argument = self._priority_to_cli_value(priority)
            except ValueError as error:
                raise ValueError(
                    f"Invalid priority '{priority}' while updating task '{task_id}' on '{clean_list}'."
                ) from error
            command.extend(["--priority", priority_argument])

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
        clean_list = self._normalize_list_name(list_name)
        return await self.get_tasks(clean_list)

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
        clean_list = self._normalize_list_name(list_name)
        tasks = await self.get_tasks(clean_list, include_completed=True)
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

    async def move_task(
        self, task_id: str, from_list: str, to_list: str
    ) -> Optional[Task]:
        cleaned_source = self._normalize_list_name(from_list)
        cleaned_target = self._normalize_list_name(to_list)
        if cleaned_source == cleaned_target:
            raise ValueError(
                f"Source and target lists are identical ('{cleaned_source}'); nothing to move."
            )

        tasks_on_source = await self.get_tasks(cleaned_source, include_completed=True)
        original_task = next(
            (task for task in tasks_on_source if task.id == task_id), None
        )
        if original_task is None:
            raise ValueError(
                f"Task '{task_id}' not found on list '{cleaned_source}'. Cannot move task."
            )

        if original_task.completed:
            raise RuntimeError(
                f"Completed task '{task_id}' cannot be moved from '{cleaned_source}'. "
                "reminders-cli only deletes incomplete tasks; mark it as incomplete first."
            )

        recreation_kwargs: Dict[str, Any] = {}
        if original_task.due_date:
            recreation_kwargs["due_date"] = original_task.due_date
        if original_task.description:
            recreation_kwargs["description"] = original_task.description
        if original_task.priority is not None:
            recreation_kwargs["priority"] = original_task.priority

        try:
            recreated_task = await self.add_task(
                original_task.title,
                list_name=cleaned_target,
                **recreation_kwargs,
            )
        except Exception as error:
            raise RuntimeError(
                f"Failed to create task '{original_task.title}' on '{cleaned_target}' "
                f"while moving from '{cleaned_source}'."
            ) from error

        recreated_task.list_name = cleaned_target

        try:
            await self._run_cli_command(["delete", cleaned_source, task_id])
        except Exception as error:
            cleanup_error: Optional[Exception] = None
            try:
                await self._run_cli_command(
                    ["delete", cleaned_target, recreated_task.id]
                )
            except Exception as attempted_cleanup_error:
                cleanup_error = attempted_cleanup_error

            if cleanup_error:
                raise RuntimeError(
                    f"Failed to delete original task '{task_id}' from '{cleaned_source}' "
                    f"and rollback of newly created task '{recreated_task.id}' on '{cleaned_target}' also failed."
                ) from error

            raise RuntimeError(
                f"Failed to delete original task '{task_id}' from '{cleaned_source}' "
                f"after recreating it on '{cleaned_target}'."
            ) from error

        return recreated_task

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
