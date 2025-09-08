from lazytask.infrastructure.mock_repository import MockTaskRepository
from lazytask.application.use_cases import (
    AddTaskUseCase,
    CompleteTaskUseCase,
    GetTaskListUseCase,
    GetAllTaskListsUseCase,
    EditTaskDateUseCase,
    MoveTaskToTomorrowUseCase,
    EditTaskDescriptionUseCase,
    EditTaskTagsUseCase,
    EditTaskPriorityUseCase,
    EditTaskFlagsUseCase,
    RefreshListUseCase,
    SortTasksUseCase,
    FilterTasksUseCase,
    GetTaskByIdUseCase,
    SearchTasksUseCase,
    GetTasksByStatusUseCase,
    GetTasksDueTodayUseCase,
    GetTasksDueTomorrowUseCase,
    GetTasksOverdueUseCase,
    GetTasksWithPriorityUseCase,
    GetTasksWithTagUseCase,
    GetTasksFlaggedUseCase
)

class DependencyContainer:
    def __init__(self):
        self.task_repository = MockTaskRepository()

        self.add_task_use_case = AddTaskUseCase(self.task_repository)
        self.complete_task_use_case = CompleteTaskUseCase(self.task_repository)
        self.get_task_list_use_case = GetTaskListUseCase(self.task_repository)
        self.get_all_task_lists_use_case = GetAllTaskListsUseCase(self.task_repository)
        self.edit_task_date_use_case = EditTaskDateUseCase(self.task_repository)
        self.move_task_to_tomorrow_use_case = MoveTaskToTomorrowUseCase(self.task_repository)
        self.edit_task_description_use_case = EditTaskDescriptionUseCase(self.task_repository)
        self.edit_task_tags_use_case = EditTaskTagsUseCase(self.task_repository)
        self.edit_task_priority_use_case = EditTaskPriorityUseCase(self.task_repository)
        self.edit_task_flags_use_case = EditTaskFlagsUseCase(self.task_repository)
        self.refresh_list_use_case = RefreshListUseCase(self.task_repository)
        self.sort_tasks_use_case = SortTasksUseCase(self.task_repository)
        self.filter_tasks_use_case = FilterTasksUseCase(self.task_repository)
        self.get_task_by_id_use_case = GetTaskByIdUseCase(self.task_repository)
        self.search_tasks_use_case = SearchTasksUseCase(self.task_repository)
        self.get_tasks_by_status_use_case = GetTasksByStatusUseCase(self.task_repository)
        self.get_tasks_due_today_use_case = GetTasksDueTodayUseCase(self.task_repository)
        self.get_tasks_due_tomorrow_use_case = GetTasksDueTomorrowUseCase(self.task_repository)
        self.get_tasks_overdue_use_case = GetTasksOverdueUseCase(self.task_repository)
        self.get_tasks_with_priority_use_case = GetTasksWithPriorityUseCase(self.task_repository)
        self.get_tasks_with_tag_use_case = GetTasksWithTagUseCase(self.task_repository)
        self.get_tasks_flagged_use_case = GetTasksFlaggedUseCase(self.task_repository)

container = DependencyContainer()
