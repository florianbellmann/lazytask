package domain

type TaskController interface {
	// Lists
	GetLists() []List
	GetListById(listId string) (List, error)

	// Tasks
	GetTaskById(taskId string) (Task, error)
	GetTasksByList(listId string) []Task

	AddTask(task Task) error
	MoveTaskToList(taskId string, targetListId string) error

	CompleteTask(taskId string) error
	UncompleteTask(taskId string) error

	UpdateTask(task Task) error
}

type TaskRepository interface {
	Save(task Task) error
}
