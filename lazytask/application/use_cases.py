from typing import List
from lazytask.domain.ports import AbstractTaskRepository
from lazytask.domain.models import Task


class AddTask:
    def __init__(self, task_repository: AbstractTaskRepository):
        self.task_repository = task_repository

    async def execute(self, title: str, list_name: str = "develop") -> Task:
        return self.task_repository.add_task(list_name, Task(title=title))


class GetAllTasks:
    def __init__(self, task_repository: AbstractTaskRepository):
        self.task_repository = task_repository

    async def execute(self, list_name: str = "develop") -> List[Task]:
        task_list = self.task_repository.get_task_list(list_name)
        if task_list:
            return task_list.tasks
        return []


class CompleteTask:
    def __init__(self, task_repository: AbstractTaskRepository):
        self.task_repository = task_repository

    async def execute(self, task_id: str, list_name: str = "develop") -> None:
        self.task_repository.complete_task(list_name, task_id)


class UpdateTask:
    def __init__(self, task_repository: AbstractTaskRepository):
        self.task_repository = task_repository

    async def execute(self, task: Task, list_name: str = "develop") -> None:
        self.task_repository.update_task(list_name, task)


class SwitchList:
    def __init__(self, task_repository: AbstractTaskRepository):
        self.task_repository = task_repository

    def execute(self, list_name: str) -> None:
        # This is not implemented in the repository, but it is not used either.
        # self.task_repository.switch_list(list_name)
        pass
