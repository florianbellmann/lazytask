from typing import List
from lazytask.domain.repository import TaskRepository
from lazytask.domain.task import Task


class AddTask:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(self, title: str) -> Task:
        return self.task_repository.add_task(title)


class GetAllTasks:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(self) -> List[Task]:
        return self.task_repository.get_all_tasks()


class CompleteTask:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(self, task_id: str) -> None:
        self.task_repository.complete_task(task_id)


class UpdateTask:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(self, task: Task) -> None:
        self.task_repository.update_task(task)


class SwitchList:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(self, list_name: str) -> None:
        self.task_repository.switch_list(list_name)