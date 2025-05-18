package entities

type Controller interface {
	// Get all task lists
	GetLists() ([]List, error)
	// Get a specific task list by its ID
	GetListById(listId string) (List, error)

	// Tasks
	GetTaskById(taskId string) (Task, error)
	// Get tasks by a specific list ID
	GetTasksByList(listId string) ([]Task, error)

	// Add a new task
	AddTask(task Task) error
	// Complete a task by its ID
	CompleteTask(taskId string) error
	// Uncomplete a task by its ID
	UncompleteTask(taskId string) error

	// Update a task
	UpdateTask(task Task) (Task, error)
	// Move task to another list
	MoveTaskToList(taskId string, targetListId string) error
}

// Interface for application state. Replicated the interface
// from the controller to avoid mismatching functionality.
// drop the alias and declare a new Repository interface
type Repository interface {
	Controller
	// Extra method to update a list for syncing
	SetList(listId string, tasks []Task) error
}

type Ui interface {
	Init() error
	Run() error
}
