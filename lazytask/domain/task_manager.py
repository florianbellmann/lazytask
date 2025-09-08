from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class Task:
    def __init__(self, id: str, title: str, completed: bool = False,
                 due_date: Optional[str] = None, description: Optional[str] = None,
                 tags: Optional[List[str]] = None, priority: Optional[int] = None,
                 flagged: Optional[bool] = None):
        self.id = id
        self.title = title
        self.completed = completed
        self.due_date = due_date
        self.description = description
        self.tags = tags if tags is not None else []
        self.priority = priority
        self.flagged = flagged

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "due_date": self.due_date,
            "description": self.description,
            "tags": self.tags,
            "priority": self.priority,
            "flagged": self.flagged,
        }

class AbstractTaskManager(ABC):
    @abstractmethod
    async def add_task(self, title: str, list_name: str = "develop") -> Task:
        """Adds a new task to the specified list."""
        pass

    @abstractmethod
    async def complete_task(self, task_id: str, list_name: str = "develop") -> Optional[Task]:
        """Marks a task as completed."""
        pass

    @abstractmethod
    async def get_tasks(self, list_name: str = "develop", include_completed: bool = False) -> List[Task]:
        """Retrieves tasks from a specified list."""
        pass

    @abstractmethod
    async def get_lists(self) -> List[str]:
        """Retrieves all available task lists."""
        pass

    @abstractmethod
    async def edit_task_date(self, task_id: str, new_date: str, list_name: str = "develop") -> Optional[Task]:
        """Edits the due date of a task."""
        pass

    @abstractmethod
    async def move_task_to_tomorrow(self, task_id: str, list_name: str = "develop") -> Optional[Task]:
        """Moves a task's due date to tomorrow."""
        pass

    @abstractmethod
    async def edit_task_description(self, task_id: str, description: str, list_name: str = "develop") -> Optional[Task]:
        """Edits the description of a task."""
        pass

    @abstractmethod
    async def edit_task_tags(self, task_id: str, tags: List[str], list_name: str = "develop") -> Optional[Task]:
        """Edits the tags of a task."""
        pass

    @abstractmethod
    async def edit_task_priority(self, task_id: str, priority: int, list_name: str = "develop") -> Optional[Task]:
        """Edits the priority of a task."""
        pass

    @abstractmethod
    async def edit_task_flag(self, task_id: str, flagged: bool, list_name: str = "develop") -> Optional[Task]:
        """Sets or unsets the flag on a task."""
        pass

    @abstractmethod
    async def refresh_tasks(self, list_name: str = "develop") -> List[Task]:
        """Refreshes the task list."""
        pass

    @abstractmethod
    async def filter_tasks(self, list_name: str = "develop", query: Optional[str] = None,
                           tags: Optional[List[str]] = None, priority: Optional[int] = None,
                           flagged: Optional[bool] = None, include_completed: bool = False) -> List[Task]:
        """Filters tasks based on various criteria."""
        pass

    @abstractmethod
    async def sort_tasks(self, list_name: str = "develop", sort_by: str = "due_date") -> List[Task]:
        """Sorts tasks based on a specified criterion."""
        pass
