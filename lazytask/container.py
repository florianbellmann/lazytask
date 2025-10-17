import os

from lazytask.infrastructure.mock_task_manager import MockTaskManager
from lazytask.infrastructure.neovim_editor import NeovimDescriptionEditor
from lazytask.application.ports.editor import DescriptionEditor
from lazytask.application.use_cases import (
    AddTask,
    GetTasks,
    CompleteTask,
    UpdateTask,
    GetLists,
    MoveTask,
)
from lazytask.domain.task_manager import TaskManager


class DependencyContainer:
    def __init__(self):
        backend_name = os.getenv("LAZYTASK_TASK_MANAGER", "mock").strip().lower()
        self.task_manager = self._create_task_manager(backend_name)
        self.description_editor: DescriptionEditor = NeovimDescriptionEditor()
        self._update_use_cases()

    def _create_task_manager(self, backend_name: str) -> TaskManager:
        if backend_name in {"", "mock"}:
            return MockTaskManager()
        if backend_name in {"reminders", "reminders_cli", "reminders-cli"}:
            from lazytask.infrastructure.reminders_cli_task_manager import (
                RemindersCliTaskManager,
            )

            return RemindersCliTaskManager()
        raise ValueError(
            f"Unknown LAZYTASK_TASK_MANAGER value '{backend_name}'. "
            "Valid options are 'mock' or 'reminders-cli'."
        )

    def set_task_manager(self, task_manager):
        self.task_manager = task_manager
        self._update_use_cases()
        return self

    def set_description_editor(self, description_editor: DescriptionEditor):
        self.description_editor = description_editor
        return self

    def get_description_editor(self) -> DescriptionEditor:
        return self.description_editor

    def _update_use_cases(self):
        self.add_task = AddTask(self.task_manager)
        self.get_tasks = GetTasks(self.task_manager)
        self.complete_task = CompleteTask(self.task_manager)
        self.update_task = UpdateTask(self.task_manager)
        self.get_lists = GetLists(self.task_manager)
        self.move_task = MoveTask(self.task_manager)

    def get(self, use_case):
        if use_case == AddTask:
            return self.add_task
        if use_case == GetTasks:
            return self.get_tasks
        if use_case == CompleteTask:
            return self.complete_task
        if use_case == UpdateTask:
            return self.update_task
        if use_case == GetLists:
            return self.get_lists
        if use_case == MoveTask:
            return self.move_task
        if use_case == DescriptionEditor:
            return self.description_editor


container = DependencyContainer()
