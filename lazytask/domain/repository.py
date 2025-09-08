from abc import ABC, abstractmethod
from typing import List, Optional

from lazytask.domain.task import Task

class TaskRepository(ABC):

    @abstractmethod
    async def add_task(self, title: str) -> Task:
        pass

    @abstractmethod
    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        pass

    @abstractmethod
    async def get_all_tasks(self) -> List[Task]:
        pass

    @abstractmethod
    async def complete_task(self, task_id: str) -> None:
        pass

    @abstractmethod
    async def update_task(self, task: Task) -> None:
        pass

    @abstractmethod
    def switch_list(self, list_name: str) -> None:
        pass