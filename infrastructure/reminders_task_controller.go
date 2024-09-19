package infrastructure

import (
	"encoding/json"
	"errors"
	"fmt"
	"lazytask/domain"
	"log"
	"os/exec"
	"slices"
	"time"
)

type Reminder struct {
	CreationDate time.Time `json:"creationDate"`
	DueDate      time.Time `json:"dueDate"`
	ExternalID   string    `json:"externalId"`
	IsCompleted  bool      `json:"isCompleted"`
	LastModified time.Time `json:"lastModified"`
	// The list id
	List     ReminderList `json:"list"`
	Notes    string       `json:"notes"`
	Priority int          `json:"priority"`
	Title    string       `json:"title"`
}

func (r Reminder) ToTask() domain.Task {
	return domain.Task{
		DueDate:     r.DueDate,
		Id:          r.ExternalID,
		IsCompleted: r.IsCompleted,
		ListId:      r.List,
		Description: r.Notes,
		Priority:    r.Priority,
		Title:       r.Title,
	}
}

func ReminderFromTask(t domain.Task) Reminder {
	return Reminder{
		DueDate:     t.DueDate,
		ExternalID:  t.Id,
		IsCompleted: t.IsCompleted,
		List:        ReminderList(t.ListId),
		Notes:       t.Description,
		Priority:    t.Priority,
		Title:       t.Title,
	}
}

type ReminderList = string

func ReminderListToList(r ReminderList) domain.List {
	return domain.List{
		Id: string(r),
		// Since the reminder list is just a string, the domain.List will have the same
		// values for id and title. We are using the name as an ID for now.
		Title: string(r),
	}
}

func ListToReminderList(l domain.List) ReminderList {
	return ReminderList(l.Id)
}

// TODO: this needs to be absolute?
// What if we move the executable to /usr/bin/local?
// use os.Getwd()
const EXECUTABLE_PATH = "adapters/reminders-cli/reminders"

// execCommand runs an external command and parses the JSON result
func execCommand[T any](commandArgs []string) (T, error) {
	commandArgs = append(commandArgs, "--format", "json")

	// Run the command
	cmd := exec.Command(EXECUTABLE_PATH, commandArgs...)
	output, err := cmd.Output()

	if err != nil {
		log.Printf("Running command: %s", cmd)
		fmt.Printf("Raw output: %s\n", string(output))
		return *new(T), fmt.Errorf("failed to run command: %w", err)
	}

	var result T
	err = json.Unmarshal(output, &result)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %s", err)
		return *new(T), err
	}

	return result, nil
}

type ReminderTaskController struct{}

func NewReminderTaskController() *ReminderTaskController {
	return &ReminderTaskController{}
}

// GetLists retrieves all task lists
func (r ReminderTaskController) GetLists() []domain.List {
	reminderLists, err := execCommand[[]ReminderList]([]string{"show-lists"})
	if err != nil {
		log.Fatalf("Failed to get lists: %s", err)
		reminderLists = []ReminderList{}
	}

	return parseLists(reminderLists)
}

func parseLists(rl []ReminderList) []domain.List {
	lists := []domain.List{}
	for _, reminderList := range rl {
		lists = append(lists, ReminderListToList(reminderList))
	}

	return lists
}

func (r ReminderTaskController) GetListById(listId string) (domain.List, error) {
	lists := r.GetLists()

	listIndex := slices.IndexFunc(lists, func(rl domain.List) bool {
		return rl.Id == listId
	})

	if listIndex == -1 {
		return domain.List{}, errors.New("List not found")
	}

	return lists[listIndex], nil
}

func (r ReminderTaskController) GetTaskById(taskId string) (domain.Task, error) {
	return domain.Task{}, errors.New("Not implemented")
}

// GetTasksByList retrieves all tasks for a specific list
func (r ReminderTaskController) GetTasksByList(listId string) []domain.Task {
	// TODO: reminders-cli can't handle lists with multiple workds yet
	// return execCommand[[]do.Task]([]string{"show", "'" + listId + "'"})
	// reminders, err := execCommand[[]Reminder]([]string{"show", "\"" + listId + "\""})
	reminders, err := execCommand[[]Reminder]([]string{"show", listId})
	if err != nil {
		log.Fatalf("Failed to get tasks for list: %s", err)
	}

	return parseTasks(reminders)
}

func parseTasks(reminders []Reminder) []domain.Task {
	tasks := []domain.Task{}
	for _, reminder := range reminders {
		tasks = append(tasks, reminder.ToTask())
	}

	return tasks
}

// AddTask adds a new task
func (r ReminderTaskController) AddTask(t domain.Task) error {
	reminder := ReminderFromTask(t)

	commandString := []string{"add", "\"" + reminder.List + "\"", "\"" + reminder.Title + "\""}

	if reminder.Notes != "" {
		commandString = append(commandString, "--notes", "\""+reminder.Notes+"\"")
	}
	if reminder.DueDate != (time.Time{}) {
		commandString = append(commandString, "--due-date", reminder.DueDate.Format("2006-01-02"))
	}

	if reminder.Priority != 0 {
		prioString := "none"
		if reminder.Priority == 1 {
			prioString = "high"
		} else if reminder.Priority > 1 {
			prioString = "medium"
		} else if reminder.Priority > 5 {
			prioString = "low"
		}
		commandString = append(commandString, "--priority", prioString)
	}

	// log.Printf("Adding task", commandString)

	_, err := execCommand[Reminder](commandString)
	if err != nil {
		return fmt.Errorf("failed to add task: %w", err)
	}

	return nil
}

// CompleteTask marks a task as completed
func (r ReminderTaskController) CompleteTask(taskId string) error {
	reminders, err := execCommand[[]Reminder]([]string{"show-all"})
	if err != nil {
		log.Fatalf("Failed to get tasks: %s", err)
	}

	reminderToCompleteIndex := slices.IndexFunc(reminders, func(r Reminder) bool {
		return r.ExternalID == taskId
	})

	if reminderToCompleteIndex == -1 {
		return errors.New("Task not found")
	}

	reminderToCompleteList := reminders[reminderToCompleteIndex].List

	_, err = execCommand[Reminder]([]string{"complete", "\"" + reminderToCompleteList + "\"", string(reminderToCompleteIndex)})

	if err != nil {
		return fmt.Errorf("failed to complete task: %w", err)
	}

	return nil
}

// UncompleteTask marks a task as uncompleted
func (r ReminderTaskController) UncompleteTask(taskId string) error {
	reminders, err := execCommand[[]Reminder]([]string{"show-all", "--only-completed"})
	if err != nil {
		log.Fatalf("Failed to get completed tasks: %s", err)
	}

	reminderToUncompleteIndex := slices.IndexFunc(reminders, func(r Reminder) bool {
		return r.ExternalID == taskId
	})

	if reminderToUncompleteIndex == -1 {
		return errors.New("Task not found")
	}

	reminderToUncompleteList := reminders[reminderToUncompleteIndex].List

	_, err = execCommand[any]([]string{"uncomplete", "\"" + reminderToUncompleteList + "\"", string(reminderToUncompleteIndex)})

	if err != nil {
		return fmt.Errorf("failed to uncomplete task: %w", err)
	}

	return nil
}

// Update a task
func (r ReminderTaskController) UpdateTask(task domain.Task) error {
	return errors.New("Not implemented")
	//
	// reminderIndex := slices.IndexFunc(r.GetTasksByList(task.ListId), func(t domain.Task) bool {
	// 	return t.Id == task.Id
	// })
	//
	// if reminderIndex == -1 {
	// 	return errors.New("Task to update not found")
	// }
	//
	// reminder := ReminderFromTask(task)
	//
	// _, err := execCommand[Reminder]([]string{"edit", "\"" + reminder.List + "\"", string(reminderIndex)})
	//
	// if err != nil {
	// 	return fmt.Errorf("Failed to update task: %w", err)
	// }
	//
	// return nil
}

// MoveTaskToList moves a task to a different list
func (r ReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {
	return errors.New("Not implemented")
	// _, err := execCommand[any]([]string{"move-task", "--task-id", taskId, "--list-id", targetListId})
	// if err != nil {
	// 	return fmt.Errorf("failed to move task: %w", err)
	// }

	// return nil
}
