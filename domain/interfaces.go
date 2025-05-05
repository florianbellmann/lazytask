package domain

type TaskController interface {
	// Lists
	GetLists() []List
	GetListById(listId string) (List, error)

	// Tasks
	GetTaskById(taskId string) (Task, error)
	GetTasksByList(listId string) []Task

	AddTask(task Task) error

	CompleteTask(taskId string) error
	UncompleteTask(taskId string) error

	UpdateTask(task Task) error
	MoveTaskToList(taskId string, targetListId string) error
}

type TaskService interface {
	// Get all task lists
	GetLists() []List
	// Get tasks by a specific list ID
	GetTasksByList(listId string) []Task

	// Add a new task
	AddTask(task Task) error
	// Complete a task by its ID
	CompleteTask(taskId string) error
	// Uncomplete a task by its ID
	UncompleteTask(taskId string) error

	// Update a task
	UpdateTask(task Task) error
	// Move task to another list
	MoveTaskToList(taskId string, targetListId string) error
}

type Ui interface {
	Init() error
	Run() error
}
