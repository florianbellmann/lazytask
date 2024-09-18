package domain

type TaskController interface {
	// Lists
	GetLists() []List
	GetListById(listId string) List

	// Tasks
	GetTaskById(taskId string) Task
	GetTasksByList(listId string) []Task

	AddTask(task Task) error
	MoveTaskToList(taskId string, targetListId string) error

	CompleteTask(taskId string) error
	UncompleteTask(taskId string) error
}
type UI interface {
	Show(tasks []Task)
}
