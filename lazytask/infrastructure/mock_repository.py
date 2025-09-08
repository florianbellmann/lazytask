from typing import List, Optional, Any
from datetime import datetime, timedelta
import uuid

from lazytask.domain.models import Task, TaskList
from lazytask.domain.ports import AbstractTaskRepository

class MockTaskRepository(AbstractTaskRepository):
    def __init__(self):
        self._task_lists: List[TaskList] = [
            TaskList(id=str(uuid.uuid4()), name="develop", tasks=[
                Task(id=str(uuid.uuid4()), title="Implement DDD structure", completed=True, created_at=datetime.now() - timedelta(days=2)),
                Task(id=str(uuid.uuid4()), title="Create MockTaskRepository", completed=True, created_at=datetime.now() - timedelta(days=1)),
                Task(id=str(uuid.uuid4()), title="Define domain models", completed=True, created_at=datetime.now() - timedelta(days=1)),
                Task(id=str(uuid.uuid4()), title="Implement Add Task feature", due_date=datetime.now() + timedelta(days=1), priority=1),
                Task(id=str(uuid.uuid4()), title="Implement Complete Task feature", due_date=datetime.now() - timedelta(days=1), priority=2, flagged=True),
                Task(id=str(uuid.uuid4()), title="Write unit tests for use cases", description="Ensure all application layer use cases are covered.", tags=["testing", "development"]),
                Task(id=str(uuid.uuid4()), title="Refactor existing scripts", due_date=datetime.now() + timedelta(days=7)),
            ]),
            TaskList(id=str(uuid.uuid4()), name="personal", tasks=[
                Task(id=str(uuid.uuid4()), title="Buy groceries", due_date=datetime.now()),
                Task(id=str(uuid.uuid4()), title="Call mom", priority=3),
            ])
        ]

    def _find_list(self, list_name: str) -> Optional[TaskList]:
        return next((tl for tl in self._task_lists if tl.name == list_name), None)

    def _find_task(self, task_list: TaskList, task_id: str) -> Optional[Task]:
        return next((t for t in task_list.tasks if t.id == task_id), None)

    def get_task_list(self, list_name: str) -> Optional[TaskList]:
        return self._find_list(list_name)

    def get_all_task_lists(self) -> List[TaskList]:
        return self._task_lists

    def add_task(self, list_name: str, task: Task) -> Task:
        task_list = self._find_list(list_name)
        if not task_list:
            raise ValueError(f"Task list '{list_name}' not found.")
        task.id = str(uuid.uuid4())
        task.created_at = datetime.now()
        task.updated_at = datetime.now()
        task_list.tasks.append(task)
        return task

    def update_task(self, list_name: str, task: Task) -> Task:
        task_list = self._find_list(list_name)
        if not task_list:
            raise ValueError(f"Task list '{list_name}' not found.")
        for i, existing_task in enumerate(task_list.tasks):
            if existing_task.id == task.id:
                task.updated_at = datetime.now()
                task_list.tasks[i] = task
                return task
        raise ValueError(f"Task with ID '{task.id}' not found in list '{list_name}'.")

    def delete_task(self, list_name: str, task_id: str) -> None:
        task_list = self._find_list(list_name)
        if not task_list:
            raise ValueError(f"Task list '{list_name}' not found.")
        task_list.tasks = [t for t in task_list.tasks if t.id != task_id]

    def complete_task(self, list_name: str, task_id: str) -> Task:
        task_list = self._find_list(list_name)
        if not task_list:
            raise ValueError(f"Task list '{list_name}' not found.")
        task = self._find_task(task_list, task_id)
        if not task:
            raise ValueError(f"Task with ID '{task_id}' not found in list '{list_name}'.")
        task.completed = True
        task.updated_at = datetime.now()
        return task

    def get_task_by_id(self, list_name: str, task_id: str) -> Optional[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return None
        return self._find_task(task_list, task_id)

    def get_tasks_by_status(self, list_name: str, completed: bool) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        return [t for t in task_list.tasks if t.completed == completed]

    def get_tasks_due_today(self, list_name: str) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        today = datetime.now().date()
        return [t for t in task_list.tasks if t.due_date and t.due_date.date() == today and not t.completed]

    def get_tasks_due_tomorrow(self, list_name: str) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        return [t for t in task_list.tasks if t.due_date and t.due_date.date() == tomorrow and not t.completed]

    def get_tasks_overdue(self, list_name: str) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        now = datetime.now()
        return [t for t in task_list.tasks if t.due_date and t.due_date < now and not t.completed]

    def get_tasks_with_priority(self, list_name: str, priority: int) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        return [t for t in task_list.tasks if t.priority == priority and not t.completed]

    def get_tasks_with_tag(self, list_name: str, tag: str) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        return [t for t in task_list.tasks if tag in t.tags and not t.completed]

    def get_tasks_flagged(self, list_name: str) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        return [t for t in task_list.tasks if t.flagged and not t.completed]

    def search_tasks(self, list_name: str, query: str) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        query_lower = query.lower()
        return [t for t in task_list.tasks if query_lower in t.title.lower() or (t.description and query_lower in t.description.lower())]

    def sort_tasks(self, list_name: str, sort_by: str, reverse: bool = False) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        
        # Filter out completed tasks for sorting, as per typical task management UIs
        tasks_to_sort = [t for t in task_list.tasks if not t.completed]

        if sort_by == "due_date":
            # Sort by due_date, placing tasks without due_date at the end
            sorted_tasks = sorted(tasks_to_sort, key=lambda t: t.due_date if t.due_date else datetime.max, reverse=reverse)
        elif sort_by == "priority":
            # Sort by priority, placing tasks without priority at the end (lower number = higher priority)
            sorted_tasks = sorted(tasks_to_sort, key=lambda t: t.priority if t.priority is not None else float('inf'), reverse=reverse)
        elif sort_by == "title":
            sorted_tasks = sorted(tasks_to_sort, key=lambda t: t.title.lower(), reverse=reverse)
        elif sort_by == "created_at":
            sorted_tasks = sorted(tasks_to_sort, key=lambda t: t.created_at, reverse=reverse)
        elif sort_by == "updated_at":
            sorted_tasks = sorted(tasks_to_sort, key=lambda t: t.updated_at, reverse=reverse)
        else:
            # Default to sorting by title if sort_by is unknown or not implemented
            sorted_tasks = sorted(tasks_to_sort, key=lambda t: t.title.lower(), reverse=reverse)
        
        return sorted_tasks

    def filter_tasks(self, list_name: str, filter_by: str, value: Any) -> List[Task]:
        task_list = self._find_list(list_name)
        if not task_list:
            return []
        
        filtered_tasks = [t for t in task_list.tasks if not t.completed] # Always filter out completed tasks

        if filter_by == "priority":
            filtered_tasks = [t for t in filtered_tasks if t.priority == value]
        elif filter_by == "tag":
            filtered_tasks = [t for t in filtered_tasks if value in t.tags]
        elif filter_by == "flagged":
            filtered_tasks = [t for t in filtered_tasks if t.flagged == value]
        elif filter_by == "due_today":
            today = datetime.now().date()
            filtered_tasks = [t for t in filtered_tasks if t.due_date and t.due_date.date() == today]
        elif filter_by == "overdue":
            now = datetime.now()
            filtered_tasks = [t for t in filtered_tasks if t.due_date and t.due_date < now]
        else:
            # If filter_by is unknown, return all non-completed tasks
            pass
        
        return filtered_tasks
