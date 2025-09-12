import uuid
from typing import List, Optional, Dict, Any
from lazytask.domain.task_manager import TaskManager
from lazytask.domain.task import Task
import datetime

class MockTaskManager(TaskManager):
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Task]] = {"develop": {}}  # list_name -> {task_id -> Task}

    async def clear_tasks(self):
        self._tasks = {"develop": {}}

    async def add_task(self, title: str, list_name: str = "develop", **kwargs) -> Task:
        if list_name not in self._tasks:
            self._tasks[list_name] = {}
        task_id = str(uuid.uuid4())
        new_task = Task(id=task_id, title=title)
        for key, value in kwargs.items():
            if hasattr(new_task, key):
                setattr(new_task, key, value)
        self._tasks[list_name][task_id] = new_task
        return new_task

    async def complete_task(self, task_id: str, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.completed = True
            return task
        return None

    async def get_tasks(self, list_name: str = "develop", include_completed: bool = False) -> List[Task]:
        if list_name not in self._tasks:
            return []
        tasks = list(self._tasks[list_name].values())
        if not include_completed:
            tasks = [task for task in tasks if not task.completed]
        return tasks

    async def get_lists(self) -> List[str]:
        return list(self._tasks.keys())

    async def edit_task_date(self, task_id: str, new_date: str, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.due_date = new_date
            return task
        return None

    async def move_task_to_tomorrow(self, task_id: str, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            task.due_date = tomorrow.isoformat()
            return task
        return None

    async def edit_task_description(self, task_id: str, description: str, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.description = description
            return task
        return None

    async def edit_task_tags(self, task_id: str, tags: List[str], list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.tags = tags
            return task
        return None

    async def edit_task_priority(self, task_id: str, priority: int, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.priority = priority
            return task
        return None

    async def edit_task_flag(self, task_id: str, flagged: bool, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.is_flagged = flagged
            return task
        return None

    async def refresh_tasks(self, list_name: str = "develop") -> List[Task]:
        # In a mock, refresh is just returning the current state
        return await self.get_tasks(list_name)

    async def filter_tasks(self, list_name: str = "develop", query: Optional[str] = None,
                           tags: Optional[List[str]] = None, priority: Optional[int] = None,
                           flagged: Optional[bool] = None, include_completed: bool = False) -> List[Task]:
        tasks = await self.get_tasks(list_name, include_completed)
        filtered_tasks = []
        for task in tasks:
            match = True
            if query and query.lower() not in task.title.lower() and \
               (task.description and query.lower() not in task.description.lower()):
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

    async def sort_tasks(self, list_name: str = "develop", sort_by: str = "due_date") -> List[Task]:
        tasks = await self.get_tasks(list_name, include_completed=True) # Sort all tasks, then filter if needed
        if sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date if t.due_date else "9999-12-31") # Sort by date, undated last
        elif sort_by == "title":
            tasks.sort(key=lambda t: t.title.lower())
        elif sort_by == "priority":
            tasks.sort(key=lambda t: t.priority if t.priority is not None else 999) # Sort by priority, no priority last
        elif sort_by == "completed":
            tasks.sort(key=lambda t: t.completed)
        return tasks

    async def edit_task_full(self, task_id: str, updates: Dict[str, Any], list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            return task
        return None

    async def set_task_recurring(self, task_id: str, recurring: str, list_name: str = "develop") -> Optional[Task]:
        if list_name in self._tasks and task_id in self._tasks[list_name]:
            task = self._tasks[list_name][task_id]
            task.recurring = recurring
            return task
        return None
