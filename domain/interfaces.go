package domain

type TaskController interface {
	// Lists
	GetLists() []List
	GetListById(id string) List

	// Tasks
	GetTaskById(id string) Task
	GetTasksByList(listId string) []Task

	AddTask(task Task)
	MoveTaskToList(task Task, list List)

	CompleteTask(task Task)
	UncompleteTask(task Task)
}
type UI interface {
	Show(tasks []Task)
}
