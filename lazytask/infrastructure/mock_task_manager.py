import datetime
import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from lazytask.domain.task import Task
from lazytask.domain.task_manager import TaskManager


class MockTaskManager(TaskManager):
    def __init__(
        self, file_path: str = "mock_tasks.json", use_persistence: bool = True
    ):
        self.file_path = file_path
        self.use_persistence = use_persistence
        self._tasks: Dict[str, Dict[str, Task]] = {
            "develop": {}
        }  # list_name -> {task_id -> Task}
        if self.use_persistence:
            self._load_tasks()

    def _normalize_list_name(self, list_name: str) -> str:
        cleaned = (list_name or "").strip()
        if not cleaned:
            raise ValueError("List name must not be empty")
        return cleaned

    def _load_tasks(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                for raw_list_name, tasks in data.items():
                    list_name = self._normalize_list_name(raw_list_name)
                    list_bucket = self._tasks.setdefault(list_name, {})
                    for task_id, task_data in tasks.items():
                        if task_data.get("due_date") and isinstance(
                            task_data.get("due_date"), str
                        ):
                            task_data["due_date"] = datetime.datetime.strptime(
                                task_data["due_date"], "%Y-%m-%d"
                            ).date()
                        if task_data.get("creation_date") and isinstance(
                            task_data.get("creation_date"), str
                        ):
                            task_data["creation_date"] = (
                                datetime.datetime.fromisoformat(
                                    task_data.pop("creation_date")
                                )
                            )
                        task_data["list_name"] = list_name
                        list_bucket[task_id] = Task(**task_data)

    def _save_tasks(self):
        if not self.use_persistence:
            return
        with open(self.file_path, "w") as f:
            data = {
                list_name: {
                    task_id: self._task_to_dict(task) for task_id, task in tasks.items()
                }
                for list_name, tasks in self._tasks.items()
            }
            json.dump(data, f, indent=4)

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        task_dict = task.__dict__.copy()
        if isinstance(task_dict.get("due_date"), datetime.date):
            task_dict["due_date"] = task_dict["due_date"].isoformat()
        if isinstance(task_dict.get("creation_date"), datetime.datetime):
            task_dict["creation_date"] = task_dict["creation_date"].isoformat()
        return task_dict

    async def clear_tasks(self):
        self._tasks = {"develop": {}}
        self._save_tasks()

    async def add_task(self, title: str, list_name: str = "develop", **kwargs) -> Task:
        list_name = self._normalize_list_name(list_name)
        if list_name not in self._tasks:
            self._tasks[list_name] = {}
        task_id = kwargs.pop("id", None) or str(uuid.uuid4())
        new_task = Task(
            id=task_id,
            title=title,
            creation_date=datetime.datetime.now(),
            list_name=list_name,
        )
        for key, value in kwargs.items():
            if hasattr(new_task, key):
                if key == "due_date" and isinstance(value, str):
                    value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                setattr(new_task, key, value)
        self._tasks[list_name][task_id] = new_task
        self._save_tasks()
        return new_task

    async def complete_task(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.completed = True
            self._save_tasks()
            return task
        return None

    async def get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name not in self._tasks:
            return []
        tasks = list(self._tasks[list_name].values())
        if not include_completed:
            tasks = [task for task in tasks if not task.completed]
        return tasks

    async def get_task(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            return self._tasks[list_name][task_id]
        return None

    async def get_lists(self) -> List[str]:
        return [name for name in self._tasks.keys()]

    async def edit_task_date(
        self, task_id: str, new_date: str, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            if isinstance(new_date, str):
                task.due_date = datetime.datetime.strptime(new_date, "%Y-%m-%d").date()
            else:
                task.due_date = new_date
            self._save_tasks()
            return task
        return None

    async def move_task_to_tomorrow(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            task.due_date = tomorrow
            self._save_tasks()
            return task
        return None

    async def edit_task_description(
        self, task_id: str, description: str, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.description = description
            self._save_tasks()
            return task
        return None

    async def edit_task_tags(
        self, task_id: str, tags: List[str], list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.tags = tags
            self._save_tasks()
            return task
        return None

    async def edit_task_priority(
        self, task_id: str, priority: int, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.priority = priority
            self._save_tasks()
            return task
        return None

    async def edit_task_flag(
        self, task_id: str, flagged: bool, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.is_flagged = flagged
            self._save_tasks()
            return task
        return None

    async def refresh_tasks(self, list_name: str = "develop") -> List[Task]:
        # In a mock, refresh is just returning the current state
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
        list_name = self._normalize_list_name(list_name)
        tasks = await self.get_tasks(list_name, include_completed)
        filtered_tasks = []
        for task in tasks:
            match = True
            if (
                query
                and query.lower() not in task.title.lower()
                and (task.description and query.lower() not in task.description.lower())
            ):
                match = False
            if tags and not any(tag in task.tags for tag in tags):
                match = False
            if priority is not None and task.priority != priority:
                match = False
            if flagged is not None and task.is_flagged != flagged:
                match = False
            if match:
                filtered_tasks.append(task)
        return filtered_tasks

    async def sort_tasks(
        self, list_name: str = "develop", sort_by: str = "due_date"
    ) -> List[Task]:
        list_name = self._normalize_list_name(list_name)
        tasks = await self.get_tasks(
            list_name, include_completed=True
        )  # Sort all tasks, then filter if needed
        if sort_by == "due_date":
            tasks.sort(
                key=lambda t: t.due_date if t.due_date else "9999-12-31"
            )  # Sort by date, undated last
        elif sort_by == "title":
            tasks.sort(key=lambda t: t.title.lower())
        elif sort_by == "priority":
            tasks.sort(
                key=lambda t: t.priority if t.priority is not None else 999
            )  # Sort by priority, no priority last
        elif sort_by == "completed":
            tasks.sort(key=lambda t: t.completed)
        return tasks

    async def edit_task_full(
        self, task_id: str, updates: Dict[str, Any], list_name: str = "develop"
    ) -> Optional[Task]:
        logging.debug(f"Editing task {task_id} with updates: {updates}")
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            for key, value in updates.items():
                if hasattr(task, key):
                    if key == "due_date" and isinstance(value, str):
                        value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                    setattr(task, key, value)
            self._save_tasks()
            return task
        return None

    async def set_task_recurring(
        self, task_id: str, recurring: str, list_name: str = "develop"
    ) -> Optional[Task]:
        list_name = self._normalize_list_name(list_name)
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.recurring = recurring
            self._save_tasks()
            return task
        return None

    async def move_task(
        self, task_id: str, from_list: str, to_list: str
    ) -> Optional[Task]:
        from_list_clean = self._normalize_list_name(from_list)
        to_list_clean = self._normalize_list_name(to_list)
        if from_list_clean in self._tasks and task_id in self._tasks[from_list_clean]:
            task = self._tasks[from_list_clean].pop(task_id)
            if to_list_clean not in self._tasks:
                self._tasks[to_list_clean] = {}
            self._tasks[to_list_clean][task_id] = task
            task.list_name = to_list_clean
            self._save_tasks()
            return task
        return None
