from abc import ABC, abstractmethod
from typing import List, Optional, Any
from datetime import datetime

from lazytask.domain.models import Task, TaskList

class AbstractTaskRepository(ABC):
    @abstractmethod
    def get_task_list(self, list_name: str) -> Optional[TaskList]:
        pass

    @abstractmethod
    def get_all_task_lists(self) -> List[TaskList]:
        pass

    @abstractmethod
    def add_task(self, list_name: str, task: Task) -> Task:
        pass

    @abstractmethod
    def update_task(self, list_name: str, task: Task) -> Task:
        pass

    @abstractmethod
    def delete_task(self, list_name: str, task_id: str) -> None:
        pass

    @abstractmethod
    def complete_task(self, list_name: str, task_id: str) -> Task:
        pass

    @abstractmethod
    def get_task_by_id(self, list_name: str, task_id: str) -> Optional[Task]:
        pass

    @abstractmethod
    def get_tasks_by_status(self, list_name: str, completed: bool) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_due_today(self, list_name: str) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_due_tomorrow(self, list_name: str) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_overdue(self, list_name: str) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_with_priority(self, list_name: str, priority: int) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_with_tag(self, list_name: str, tag: str) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_flagged(self, list_name: str) -> List[Task]:
        pass

    @abstractmethod
    def search_tasks(self, list_name: str, query: str) -> List[Task]:
        pass

    @abstractmethod
    def sort_tasks(self, list_name: str, sort_by: str, reverse: bool) -> List[Task]:
        pass

    @abstractmethod
    def filter_tasks(self, list_name: str, filter_by: str, value: Any) -> List[Task]:
        pass
