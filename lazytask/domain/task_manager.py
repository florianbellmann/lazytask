from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from lazytask.domain.task import Task


class TaskManager(ABC):
    @abstractmethod
    async def add_task(self, title: str, list_name: str = "develop") -> Task:
        """Adds a new task to the specified list."""
        pass

    @abstractmethod
    async def complete_task(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        """Marks a task as completed."""
        pass

    @abstractmethod
    async def get_tasks(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        """Retrieves tasks from a specified list."""
        pass

    @abstractmethod
    async def get_lists(self) -> List[str]:
        """Retrieves all available task lists."""
        pass

    @abstractmethod
    async def edit_task_date(
        self, task_id: str, new_date: str, list_name: str = "develop"
    ) -> Optional[Task]:
        """Edits the due date of a task."""
        pass

    @abstractmethod
    async def move_task_to_tomorrow(
        self, task_id: str, list_name: str = "develop"
    ) -> Optional[Task]:
        """Moves a task's due date to tomorrow."""
        pass

    @abstractmethod
    async def edit_task_description(
        self, task_id: str, description: str, list_name: str = "develop"
    ) -> Optional[Task]:
        """Edits the description of a task."""
        pass

    @abstractmethod
    async def edit_task_tags(
        self, task_id: str, tags: List[str], list_name: str = "develop"
    ) -> Optional[Task]:
        """Edits the tags of a task."""
        pass

    @abstractmethod
    async def edit_task_priority(
        self, task_id: str, priority: int, list_name: str = "develop"
    ) -> Optional[Task]:
        """Edits the priority of a task."""
        pass

    @abstractmethod
    async def edit_task_flag(
        self, task_id: str, flagged: bool, list_name: str = "develop"
    ) -> Optional[Task]:
        """Sets or unsets the flag on a task."""
        pass

    @abstractmethod
    async def refresh_tasks(self, list_name: str = "develop") -> List[Task]:
        """Refreshes the task list."""
        pass

    @abstractmethod
    async def filter_tasks(
        self,
        list_name: str = "develop",
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[int] = None,
        flagged: Optional[bool] = None,
        include_completed: bool = False,
    ) -> List[Task]:
        """Filters tasks based on various criteria."""
        pass

    @abstractmethod
    async def sort_tasks(
        self, list_name: str = "develop", sort_by: str = "due_date"
    ) -> List[Task]:
        """Sorts tasks based on a specified criterion."""
        pass

    @abstractmethod
    async def edit_task_full(
        self, task_id: str, updates: Dict[str, Any], list_name: str = "develop"
    ) -> Optional[Task]:
        """Edits multiple fields of a task at once."""
        pass

    @abstractmethod
    async def set_task_recurring(
        self, task_id: str, recurring: str, list_name: str = "develop"
    ) -> Optional[Task]:
        """Sets the recurring rule for a task."""
        pass
