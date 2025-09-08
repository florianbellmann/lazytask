import datetime
import uuid
from typing import Dict, List, Optional

from lazytask.domain.repository import TaskRepository
from lazytask.domain.task import Task


class MockTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, Task]] = {"develop": {}}
        self._current_list = "develop"

    async def add_task(self, title: str) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, title=title)
        self._tasks[self._current_list][task_id] = task
        return task

    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self._tasks[self._current_list].get(task_id)

    async def get_all_tasks(self) -> List[Task]:
        return list(self._tasks[self._current_list].values())

    async def complete_task(self, task_id: str) -> None:
        task = await self.get_task_by_id(task_id)
        if task:
            task.completed = True

    async def update_task(self, task: Task) -> None:
        if task.id in self._tasks[self._current_list]:
            self._tasks[self._current_list][task.id] = task

    def switch_list(self, list_name: str) -> None:
        self._current_list = list_name
        if list_name not in self._tasks:
            self._tasks[list_name] = {}