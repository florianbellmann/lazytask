import datetime
import uuid
from typing import Dict, List, Optional

from lazytask.domain.repository import TaskRepository
from lazytask.domain.task import Task


class MockTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._current_list = "develop"

    def add_task(self, title: str) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, title=title)
        self._tasks[task_id] = task
        return task

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def complete_task(self, task_id: str) -> None:
        task = self.get_task_by_id(task_id)
        if task:
            task.completed = True

    def update_task(self, task: Task) -> None:
        if task.id in self._tasks:
            self._tasks[task.id] = task

    def switch_list(self, list_name: str) -> None:
        self._current_list = list_name
