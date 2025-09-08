from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from lazytask.domain.task import Task

class Backend(ABC):
    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        pass

    @abstractmethod
    def add_task(self, title: str) -> Task:
        pass

    @abstractmethod
    def complete_task(self, task_id: UUID) -> Task:
        pass

    @abstractmethod
    def update_task(self, task: Task) -> Task:
        pass
