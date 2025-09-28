import logging
from typing import List, Optional, Dict, Any
from lazytask.domain.task_manager import TaskManager
from lazytask.domain.task import Task


class AddTask:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(self, title: str, list_name: str = "develop", **kwargs) -> Task:
        return await self.task_manager.add_task(title, list_name, **kwargs)


class GetTasks:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(
        self, list_name: str = "develop", include_completed: bool = False
    ) -> List[Task]:
        return await self.task_manager.get_tasks(list_name, include_completed)


class CompleteTask:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(self, task_id: str, list_name: str = "develop") -> Optional[Task]:
        return await self.task_manager.complete_task(task_id, list_name)


class UpdateTask:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(
        self, task_id: str, updates: Dict[str, Any], list_name: str = "develop"
    ) -> Optional[Task]:
        return await self.task_manager.edit_task_full(task_id, updates, list_name)


class GetLists:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(self) -> List[str]:
        return await self.task_manager.get_lists()
