from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from lazytask.domain.backend import Backend
from lazytask.domain.task import Task

class MockBackend(Backend):
    def __init__(self):
        self.tasks: List[Task] = [
            Task(
                title="Task 1",
                description="This is the first task",
                tags=["work"],
                priority=1,
                due_date=datetime.now() + timedelta(days=1),
                flagged=True,
                recurring="daily",
            ),
            Task(
                title="Task 2",
                description="This is the second task",
                tags=["home"],
                priority=2,
                due_date=datetime.now() + timedelta(days=2),
            ),
            Task(
                title="Task 3",
                completed=True,
                description="This is the third task",
                tags=["work", "urgent"],
                priority=3,
                due_date=datetime.now() - timedelta(days=1),
                flagged=True,
            ),
        ]

    def get_all_tasks(self) -> List[Task]:
        return self.tasks

    def add_task(self, title: str) -> Task:
        new_task = Task(title=title)
        self.tasks.append(new_task)
        return new_task

    def complete_task(self, task_id: UUID) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                return task
        raise ValueError(f"Task with id {task_id} not found")

    def update_task(self, updated_task: Task) -> Task:
        for i, task in enumerate(self.tasks):
            if task.id == updated_task.id:
                self.tasks[i] = updated_task
                return updated_task
        raise ValueError(f"Task with id {updated_task.id} not found")
